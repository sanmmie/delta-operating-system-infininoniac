# test_client.py
import asyncio
import json
import websockets
from uuid import uuid4

KERNE_URI = "ws://localhost:8765"

async def run():
    async with websockets.connect(KERNE_URI) as ws:
        # Example: ask the heritage node for artifact by id
        request_id = str(uuid4())
        msg = {
            "type": "query_artifact",
            "request_id": request_id,
            "q": {"id": "artifact_sample_001"}
        }
        await ws.send(json.dumps(msg))
        # read response(s)
        try:
            async for raw in ws:
                print("RECV:", raw)
                break
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    asyncio.run(run())
