#!/usr/bin/env python3
"""
kernel-mock.py — minimal Δ kernel mock / router

Purpose:
- Accept websocket connections from nodes and clients.
- Nodes register using {"type":"register_node","node_id": "...", "domain":"..."}.
- Clients send messages targeted to a node via {"to": "<node_id>", "payload": {...}} or broadcast when "to" omitted.
- Designed for local development and CI integration. Not for production.

Usage:
$ python kernel-mock.py --host 0.0.0.0 --port 8765
"""
import asyncio
import json
import logging
import argparse
import websockets

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
LOG = logging.getLogger("kernel-mock")

# node_id -> websocket
REGISTERED_NODES = {}

async def handle_connection(ws, path):
    """
    Each client (node or test client) connects and can send JSON messages.
    A node registers: {"type":"register_node","node_id":"heritage-node-1","domain":"heritage.culture"}
    Messages forwarded:
      - If message contains "to": "<node_id>", route to that node (if registered).
      - If no "to": broadcast to all nodes.
    Responses from nodes will be passed back to the sender only when they include "reply_to".
    """
    peer = ws.remote_address
    LOG.info("Conn from %s", peer)
    try:
        async for raw in ws:
            try:
                msg = json.loads(raw)
            except Exception:
                LOG.warning("Non-json message: %s", raw)
                continue

            mtype = msg.get("type")
            if mtype == "register_node":
                node_id = msg.get("node_id")
                domain = msg.get("domain")
                if not node_id:
                    await ws.send(json.dumps({"type":"error","reason":"missing_node_id"}))
                    continue
                REGISTERED_NODES[node_id] = ws
                LOG.info("Registered node %s domain=%s", node_id, domain)
                await ws.send(json.dumps({"type":"register_ack","node_id":node_id}))
                continue

            # Routing logic
            to = msg.get("to")
            if to:
                target = REGISTERED_NODES.get(to)
                if target:
                    try:
                        await target.send(json.dumps(msg.get("payload", msg)))
                        LOG.debug("Routed message to %s", to)
                    except Exception as e:
                        LOG.exception("Failed forward to %s: %s", to, e)
                        await ws.send(json.dumps({"type":"error","reason":"forward_failed","details":str(e)}))
                else:
                    # not found
                    await ws.send(json.dumps({"type":"error","reason":"node_not_registered","node_id":to}))
            else:
                # broadcast to all nodes
                coros = []
                for nid, node_ws in list(REGISTERED_NODES.items()):
                    if node_ws.closed:
                        REGISTERED_NODES.pop(nid, None)
                        continue
                    coros.append(node_ws.send(json.dumps(msg.get("payload", msg))))
                if coros:
                    await asyncio.gather(*coros, return_exceptions=True)
                    LOG.debug("Broadcasted message to %d nodes", len(coros))
    except websockets.exceptions.ConnectionClosed:
        LOG.info("Connection closed %s", peer)
    finally:
        # clean up any registered node entries for this websocket
        stale = [nid for nid, w in REGISTERED_NODES.items() if w == ws]
        for nid in stale:
            REGISTERED_NODES.pop(nid, None)
            LOG.info("Unregistered node %s (disconnected)", nid)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    start = websockets.serve(handle_connection, args.host, args.port)
    LOG.info("Starting kernel mock on %s:%d", args.host, args.port)
    asyncio.get_event_loop().run_until_complete(start)
    asyncio.get_event_loop().run_forever()
