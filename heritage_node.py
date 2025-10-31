# heritage_node.py
"""
Minimal Delta Heritage Node
- Registers with Δ kernel
- Responds to 'query_artifact' requests with a simple JSON payload
"""
import asyncio
import json
import websockets
import os
import uuid
from datetime import datetime

DELTANET_URI = os.getenv("DELTANET_URI", "ws://localhost:8765")  # kernel websocket

NODE_ID = f"heritage-node-{uuid.uuid4().hex[:8]}"

async def register(ws):
    msg = {
        "type": "register_node",
        "node_id": NODE_ID,
        "domain": "heritage.culture",
        "capabilities": ["query_artifact", "ingest_artifact", "list_collections"]
    }
    await ws.send(json.dumps(msg))

async def handle_message(ws, raw):
    try:
        msg = json.loads(raw)
    except Exception:
        return
    mtype = msg.get("type")
    # Example query: {"type": "query_artifact", "request_id": "abc", "q": {"id": "artifact_1"}}
    if mtype == "query_artifact":
        request_id = msg.get("request_id")
        q = msg.get("q", {})
        artifact_id = q.get("id", "sample_001")
        # In production: fetch from Supabase or other storage
        artifact = {
            "id": artifact_id,
            "title": "Òrò Àtijọ́ — Oral History Sample",
            "language": "yoruba",
            "summary": "Recorded folktale about the sacred market.",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "assets": [
                {"type": "audio", "url": "https://your.cdn/asset/sample_001.mp3"},
                {"type": "text", "url": "https://your.api/artifact/sample_001/text"}
            ],
            "provenance": {"collected_by": "community_archivist", "consent": True}
        }
        resp = {
            "type": "query_response",
            "request_id": request_id,
            "node_id": NODE_ID,
            "status": "ok",
            "artifact": artifact
        }
        await ws.send(json.dumps(resp))

async def run():
    async with websockets.connect(DELTANET_URI) as ws:
        await register(ws)
        async for raw in ws:
            await handle_message(ws, raw)

if __name__ == "__main__":
    asyncio.run(run())
