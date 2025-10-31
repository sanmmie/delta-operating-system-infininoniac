"""
heritage_node_full.py
Delta Heritage Node - full version with Supabase integration.

Features:
- Registers with Δ kernel over websocket
- Responds to: query_artifact, ingest_artifact, list_collections, list_artifacts, get_presigned_asset
- Uses Supabase for persistence (artifacts, collections, assets, consents)
- Minimal validation, error responses, and audit logging
- Env-configurable (SUPABASE_URL, SUPABASE_KEY, DELTANET_URI, NODE_NAME)

How to use:
- Provide SUPABASE_URL & SUPABASE_KEY (service role key recommended)
- Start Δ kernel or point DELTANET_URI to a running orchestrator
- Run: python heritage_node_full.py
"""
import os
import asyncio
import json
import uuid
import logging
from datetime import datetime, timedelta

import websockets
from dotenv import load_dotenv

# Supabase python client (blocking). We'll call it via asyncio.to_thread to avoid blocking the event loop.
from supabase import create_client, Client as SupabaseClient

load_dotenv()

# -- Configuration (from env) --
DELTANET_URI = os.getenv("DELTANET_URI", "ws://localhost:8765")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
NODE_NAME = os.getenv("NODE_NAME", f"heritage-node-{uuid.uuid4().hex[:8]}")
SIGNED_URL_EXPIRY_SECONDS = int(os.getenv("SIGNED_URL_EXPIRY_SECONDS", "3600"))

# Basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("heritage_node")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.warning("SUPABASE_URL and SUPABASE_KEY are not set. Node will fail on DB operations.")

# Initialize supabase client (blocking). We'll call it inside executor when needed.
_supabase_client: SupabaseClient | None = None


def get_supabase_client() -> SupabaseClient:
    global _supabase_client
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError("Supabase URL/KEY not configured in env")
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client


# -------------------------
# Utility helpers (async-friendly)
# -------------------------
async def supabase_insert(table: str, data: dict):
    """Insert a row into supabase table (runs in thread)."""
    def _insert():
        client = get_supabase_client()
        return client.table(table).insert(data).execute()
    return await asyncio.to_thread(_insert)


async def supabase_select(table: str, query: dict | None = None, limit: int = 100):
    def _select():
        client = get_supabase_client()
        q = client.table(table).select("*")
        if query:
            for k, v in query.items():
                if isinstance(v, dict) and v.get("op") == "ilike":
                    q = q.ilike(k, v["value"])
                else:
                    q = q.eq(k, v)
        q = q.limit(limit)
        return q.execute()
    return await asyncio.to_thread(_select)


async def supabase_get_by_id(table: str, id_value):
    def _get():
        client = get_supabase_client()
        return client.table(table).select("*").eq("id", id_value).single().execute()
    return await asyncio.to_thread(_get)


async def supabase_create_signed_url(bucket: str, path: str, expires: int = SIGNED_URL_EXPIRY_SECONDS):
    def _signed():
        client = get_supabase_client()
        # create_signed_url returns {'signedURL': ..., 'error': None} in many supabase clients
        return client.storage.from_(bucket).create_signed_url(path, expires)
    return await asyncio.to_thread(_signed)


# -------------------------
# Message handling
# -------------------------
async def register(ws):
    msg = {
        "type": "register_node",
        "node_id": NODE_NAME,
        "domain": "heritage.culture",
        "capabilities": ["query_artifact", "ingest_artifact", "list_collections", "list_artifacts", "get_presigned_asset"],
        "metadata": {
            "name": "Heritage Node (Yorùbá)",
            "maintainer": NODE_NAME,
            "version": "0.2"
        }
    }
    await ws.send(json.dumps(msg))
    logger.info("Registered node with kernel: %s", NODE_NAME)


async def respond_error(ws, request_id, reason="error", details=None):
    payload = {
        "type": "error",
        "request_id": request_id,
        "node_id": NODE_NAME,
        "status": "error",
        "reason": reason,
        "details": details or {}
    }
    await ws.send(json.dumps(payload))


async def handle_query_artifact(ws, msg):
    request_id = msg.get("request_id")
    q = msg.get("q", {})
    artifact_id = q.get("id")
    try:
        if not artifact_id:
            await respond_error(ws, request_id, "bad_request", {"message": "artifact id required"})
            return

        res = await supabase_get_by_id("artifacts", artifact_id)
        if res and res.data:
            artifact = res.data
            # fetch assets for artifact
            assets_res = await supabase_select("assets", {"artifact_id": artifact_id})
            assets = assets_res.data if assets_res and getattr(assets_res, "data", None) is not None else []
            artifact["assets"] = assets
            resp = {
                "type": "query_response",
                "request_id": request_id,
                "node_id": NODE_NAME,
                "status": "ok",
                "artifact": artifact
            }
            await ws.send(json.dumps(resp))
            logger.info("Replied artifact %s", artifact_id)
        else:
            await respond_error(ws, request_id, "not_found", {"artifact_id": artifact_id})
    except Exception as e:
        logger.exception("Failed query_artifact")
        await respond_error(ws, request_id, "internal_error", {"error": str(e)})


async def handle_list_collections(ws, msg):
    request_id = msg.get("request_id")
    try:
        res = await supabase_select("collections", limit=200)
        collections = res.data if res and getattr(res, "data", None) is not None else []
        resp = {
            "type": "list_collections_response",
            "request_id": request_id,
            "node_id": NODE_NAME,
            "status": "ok",
            "collections": collections
        }
        await ws.send(json.dumps(resp))
        logger.info("Sent collections list (count=%d)", len(collections))
    except Exception as e:
        logger.exception("Failed list_collections")
        await respond_error(ws, request_id, "internal_error", {"error": str(e)})


async def handle_list_artifacts(ws, msg):
    request_id = msg.get("request_id")
    q = msg.get("q", {})
    try:
        # support optional text search on title or summary (ilike)
        query = None
        if q and q.get("text"):
            query = {"title": {"op": "ilike", "value": f"%{q['text']}%"}}
        res = await supabase_select("artifacts", query=query, limit=200)
        artifacts = res.data if res and getattr(res, "data", None) is not None else []
        resp = {
            "type": "list_artifacts_response",
            "request_id": request_id,
            "node_id": NODE_NAME,
            "status": "ok",
            "artifacts": artifacts
        }
        await ws.send(json.dumps(resp))
        logger.info("Sent artifacts list (count=%d)", len(artifacts))
    except Exception as e:
        logger.exception("Failed list_artifacts")
        await respond_error(ws, request_id, "internal_error", {"error": str(e)})


async def handle_ingest_artifact(ws, msg):
    """
    Expected message:
    {
        "type": "ingest_artifact",
        "request_id": "req-123",
        "artifact": {
            "title": "...",
            "language": "yoruba",
            "summary": "...",
            "collection_id": "...",
            "assets": [
                {"bucket": "heritage", "path": "audio/abc.mp3", "type": "audio", "label": "..."},
                ...
            ],
            "provenance": {...}
        },
        "consent": {"consented_by": "name", "consent_record_url": "..."}
    }
    """
    request_id = msg.get("request_id")
    payload = msg.get("artifact", {})
    consent = msg.get("consent", {})
    try:
        # persist artifact
        artifact_id = payload.get("id") or f"artifact_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow().isoformat() + "Z"
        artifact_row = {
            "id": artifact_id,
            "title": payload.get("title"),
            "language": payload.get("language", "yoruba"),
            "summary": payload.get("summary"),
            "collection_id": payload.get("collection_id"),
            "created_at": now,
            "metadata": payload.get("metadata", {}),
            "provenance": payload.get("provenance", {})
        }
        insert_res = await supabase_insert("artifacts", artifact_row)
        # insert assets if present
        assets = payload.get("assets", [])
        assets_inserted = []
        for a in assets:
            asset_row = {
                "id": a.get("id") or f"asset_{uuid.uuid4().hex[:10]}",
                "artifact_id": artifact_id,
                "bucket": a.get("bucket"),
                "path": a.get("path"),
                "type": a.get("type"),
                "label": a.get("label"),
                "created_at": now
            }
            await supabase_insert("assets", asset_row)
            assets_inserted.append(asset_row)

        # persist consent record
        if consent:
            consent_row = {
                "id": consent.get("id") or f"consent_{uuid.uuid4().hex[:10]}",
                "artifact_id": artifact_id,
                "consented_by": consent.get("consented_by"),
                "consent_record_url": consent.get("consent_record_url"),
                "created_at": now
            }
            await supabase_insert("consents", consent_row)

        resp = {
            "type": "ingest_response",
            "request_id": request_id,
            "node_id": NODE_NAME,
            "status": "ok",
            "artifact_id": artifact_id,
            "assets": assets_inserted
        }
        await ws.send(json.dumps(resp))
        logger.info("Ingested artifact %s (assets=%d)", artifact_id, len(assets_inserted))
    except Exception as e:
        logger.exception("Failed ingest_artifact")
        await respond_error(ws, request_id, "internal_error", {"error": str(e)})


async def handle_get_presigned_asset(ws, msg):
    """
    Request:
    {
        "type": "get_presigned_asset",
        "request_id": "req-1",
        "q": {"artifact_id": "artifact_...", "asset_id": "asset_..."}
    }
    Response:
    {
        "type": "get_presigned_asset_response",
        "request_id": "...",
        "node_id": "...",
        "status": "ok",
        "signed_url": "https://..."
    }
    """
    request_id = msg.get("request_id")
    q = msg.get("q", {})
    artifact_id = q.get("artifact_id")
    asset_id = q.get("asset_id")
    try:
        if not asset_id:
            await respond_error(ws, request_id, "bad_request", {"message": "asset_id required"})
            return
        res = await supabase_get_by_id("assets", asset_id)
        if not res or not getattr(res, "data", None):
            await respond_error(ws, request_id, "not_found", {"asset_id": asset_id})
            return
        asset = res.data
        bucket = asset.get("bucket")
        path = asset.get("path")
        if not bucket or not path:
            await respond_error(ws, request_id, "bad_request", {"message": "asset missing bucket/path"})
            return
        signed_res = await supabase_create_signed_url(bucket, path, SIGNED_URL_EXPIRY_SECONDS)
        # supabase client returns dict with 'signedURL' or 'signed_url' depending on version
        signed_url = None
        if isinstance(signed_res, dict):
            signed_url = signed_res.get("signedURL") or signed_res.get("signed_url") or signed_res.get("data", {}).get("signedURL")
        else:
            # many supabase-py versions return an object with .get("signedURL")
            try:
                signed_url = signed_res.get("signedURL")
            except Exception:
                signed_url = None

        if not signed_url:
            await respond_error(ws, request_id, "internal_error", {"message": "failed to create signed URL", "raw": signed_res})
            return

        resp = {
            "type": "get_presigned_asset_response",
            "request_id": request_id,
            "node_id": NODE_NAME,
            "status": "ok",
            "signed_url": signed_url,
            "expires_in": SIGNED_URL_EXPIRY_SECONDS
        }
        await ws.send(json.dumps(resp))
        logger.info("Provided signed URL for asset %s", asset_id)
    except Exception as e:
        logger.exception("Failed get_presigned_asset")
        await respond_error(ws, request_id, "internal_error", {"error": str(e)})


async def handle_message(ws, raw):
    try:
        msg = json.loads(raw)
    except Exception:
        logger.warning("Received non-json message")
        return

    mtype = msg.get("type")
    # route messages
    if mtype == "query_artifact":
        await handle_query_artifact(ws, msg)
    elif mtype == "ingest_artifact":
        await handle_ingest_artifact(ws, msg)
    elif mtype == "list_collections":
        await handle_list_collections(ws, msg)
    elif mtype == "list_artifacts":
        await handle_list_artifacts(ws, msg)
    elif mtype == "get_presigned_asset":
        await handle_get_presigned_asset(ws, msg)
    elif mtype == "ping":
        # simple keepalive
        await ws.send(json.dumps({"type": "pong", "node_id": NODE_NAME, "ts": datetime.utcnow().isoformat() + "Z"}))
    else:
        # unknown message type -> ignore or send a hint
        if msg.get("request_id"):
            await respond_error(ws, msg.get("request_id"), "unsupported", {"message": f"unsupported message type: {mtype}"})
        else:
            logger.debug("Ignored message type: %s", mtype)


async def run():
    backoff = 1
    while True:
        try:
            logger.info("Connecting to Δ kernel at %s", DELTANET_URI)
            async with websockets.connect(DELTANET_URI, ping_interval=20, ping_timeout=10) as ws:
                await register(ws)
                backoff = 1
                async for raw in ws:
                    # received a raw text message
                    await handle_message(ws, raw)
        except Exception as e:
            logger.exception("Connection error or disconnected: %s", str(e))
            logger.info("Reconnecting in %d seconds...", backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("Heritage node shutting down (KeyboardInterrupt)")
