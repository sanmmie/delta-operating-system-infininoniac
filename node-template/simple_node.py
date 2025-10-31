
**3) `node-template/simple_node.py`**

```python
#!/usr/bin/env python3
"""
simple_node.py — minimal example node for local dev

- Connects to kernel-mock (ws://127.0.0.1:8765)
- Registers as 'heritage-node-local'
- Replies to 'query_artifact' messages with a simple stubbed artifact
"""
import asyncio
import json
import websockets
import uuid
from datetime import datetime

KERNEL_URI = "ws://127.0.0.1:8765"
NODE_ID = "heritage-node-local"

async def register(ws):
    msg = {"type": "register_node", "node_id": NODE_ID, "domain": "heritage.culture"}
    await ws.send(json.dumps(msg))
    # wait for ack optionally
    raw = await ws.recv()
    try:
        j = json.loads(raw)
        print("Received:", j)
    except Exception:
        print("Raw:", raw)

async def handle_message(ws, raw):
    msg = json.loads(raw)
    mtype = msg.get("type")
    if mtype == "query_artifact":
        req = msg.get("request_id")
        q = msg.get("q", {})
        artifact_id = q.get("id", "sample_001")
        resp = {
            "type": "query_response",
            "request_id": req,
            "node_id": NODE_ID,
            "status": "ok",
            "artifact": {
                "id": artifact_id,
                "title": "Stubbed Artifact",
                "summary": "This is a stub response from simple_node.",
                "language": "yoruba",
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
        }
        await ws.send(json.dumps(resp))
    elif mtype == "ping":
        await ws.send(json.dumps({"type":"pong","node_id":NODE_ID}))

async def run():
    async with websockets.connect(KERNEL_URI) as ws:
        await register(ws)
        async for raw in ws:
            # messages from kernel (could be client messages forwarded)
            await handle_message(ws, raw)

if __name__ == "__main__":
    asyncio.run(run())
