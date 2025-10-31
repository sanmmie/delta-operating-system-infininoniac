#!/usr/bin/env python3
"""
test_client.py — send a message to a node via kernel-mock

Sends a message with "to": "<node_id>" so kernel-mock routes it to the node.
"""
import asyncio
import json
import websockets
import uuid

KERNEL_URI = "ws://127.0.0.1:8765"
TARGET_NODE = "heritage-node-local"

async def run():
    async with websockets.connect(KERNEL_URI) as ws:
        request_id = str(uuid.uuid4())
        message = {
            "to": TARGET_NODE,
            "payload": {
                "type": "query_artifact",
                "request_id": request_id,
                "q": {"id": "artifact_sample_001"}
            }
        }
        await ws.send(json.dumps(message))
        # optionally wait to receive a response (kernel mock does not forward responses to client by default,
        # so if you want responses echoed back, modify kernel-mock to forward 'reply_to' keys)
        try:
            raw = await ws.recv()
            print("Received:", raw)
        except Exception as e:
            print("No response:", e)

if __name__ == "__main__":
    asyncio.run(run())
