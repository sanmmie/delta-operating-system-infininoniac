# node-template

Purpose: a minimal template developers can copy to create a Δ node.

Quickstart:
1. Install deps: `pip install websockets`
2. Start kernel mock: `python ../kernel-mock.py`
3. Run the node: `python simple_node.py`
4. Use `test_client.py` (see below) to send messages to the node.

Message contract (simplified)
- Register:
  ```json
  { "type": "register_node", "node_id": "heritage-node-1", "domain": "heritage.culture" }
