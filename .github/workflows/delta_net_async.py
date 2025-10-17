
### **2. delta_net_async.py**
```python
"""
Delta Operating System - Consciousness Conductor
Phase III: Async Multi-Node Coordination
"""

from __future__ import annotations
import asyncio
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
import datetime
import logging
import random

# Import delta prototype if available; otherwise include minimal inline fallback
try:
    from delta_os_prototype import DeltaOS, DeltaEngine, ContextCompiler, TransformationPlan
except Exception:
    # Minimal fallback definitions
    from dataclasses import dataclass, field

    @dataclass
    class TransformationPlan:
        actions: List[Dict[str, Any]] = field(default_factory=list)
        rationale: str = ""
        confidence: float = 0.0

    class DeltaEngine:
        def __init__(self, sensitivity: float = 0.02):
            self.sensitivity = sensitivity

        def compute_delta(self, input_data, history):
            prev = history[-1].get("market_index", 0.0) if history else input_data.get("market_index", 0.0)
            curr = input_data.get("market_index", prev)
            delta = curr - prev
            denom = max(abs(prev), 1.0)
            normalized = delta / denom
            return {"delta": delta, "normalized": normalized, "prev": prev, "curr": curr}

        def generate_transformation_map(self, delta_info, context):
            d = delta_info["normalized"]
            actions = []
            rationale = ""
            confidence = min(0.95, max(0.05, abs(d)))
            if d > self.sensitivity:
                actions.append({"type": "increase_allocation", "target": "equities", "magnitude": min(0.2, d)})
                rationale = "Market trending up; opportunistic increase."
            elif d < -self.sensitivity:
                actions.append({"type": "decrease_allocation", "target": "equities", "magnitude": min(0.2, -d)})
                rationale = "Market trending down; defensive posture."
            else:
                actions.append({"type": "hold", "target": "portfolio", "magnitude": 0.0})
                rationale = "No strong trend; maintain position."
            risk = float(context.get("risk_tolerance", 0.5)) if isinstance(context, dict) else 0.5
            for a in actions:
                a["adjusted_magnitude"] = a.get("magnitude", 0.0) * (1.0 - risk)
            return TransformationPlan(actions=actions, rationale=rationale, confidence=confidence)

    class ContextCompiler:
        def compile(self, raw_env):
            ts = datetime.datetime.utcnow()
            env = dict(raw_env)
            env.setdefault("risk_tolerance", 0.5)
            env.setdefault("ethical_constraints", {})
            return type("CTX", (), {"env": env, "timestamp": ts, "summary": lambda self=None: {**env, "ts": ts.isoformat()}})()

    class DeltaOS:
        def __init__(self, intent: Dict[str, Any]):
            self.kernel_delta = DeltaEngine()
            self.compiler = ContextCompiler()
            self.integrator = None
            self.modules = type("M", (), {"history": [], "observe": lambda self, x: self.history.append(dict(x)) or {"pattern_map": x}, "reflect": (lambda self, r: {"timestamp": datetime.datetime.utcnow().isoformat(), "success": False, "notes": "fallback"})})()
            self.transmission = type("T", (), {"nodes": {}, "register_node": lambda self, nid, sig: self.nodes.update({nid: sig.summary()}), "sync_context": lambda self, a, b: {**self.nodes.get(a, {}), **self.nodes.get(b, {})}})()
            self.intent = intent
            self.cycle_log = []

        def init_node(self, node_id: str, raw_env: Dict[str, Any]):
            ctx = self.compiler.compile(raw_env)
            self.transmission.register_node(node_id, ctx)
            return ctx

        def run_cycle(self, input_data, raw_env, node_id: Optional[str] = None):
            self.modules.observe(input_data)
            context = self.compiler.compile(raw_env)
            delta_info = self.kernel_delta.compute_delta(input_data, self.modules.history[:-1])
            plan = self.kernel_delta.generate_transformation_map(delta_info, context)
            plan_d = asdict(plan)
            cycle_record = {"timestamp": datetime.datetime.utcnow().isoformat(), "input": input_data, "context": context.summary(), "delta_info": delta_info, "plan": plan_d, "intent_score": 0.5}
            feedback = self.modules.reflect(cycle_record)
            self.cycle_log.append({"cycle": len(self.cycle_log)+1, "record": cycle_record, "feedback": feedback})
            if node_id:
                self.transmission.register_node(node_id, context)
            return cycle_record, feedback

# Setup logging
LOG = logging.getLogger("delta_net_async")
LOG.setLevel(logging.INFO)
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
LOG.addHandler(_handler)

class InMemoryTransport:
    """A simple pub/sub transport for exchanging context between nodes"""
    def __init__(self):
        self.subscribers: Dict[str, asyncio.Queue] = {}

    async def register(self, node_id: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self.subscribers[node_id] = q
        LOG.debug(f"transport: registered {node_id}")
        return q

    async def unregister(self, node_id: str) -> None:
        self.subscribers.pop(node_id, None)
        LOG.debug(f"transport: unregistered {node_id}")

    async def publish(self, src_node: str, message: Dict[str, Any]) -> None:
        for nid, q in self.subscribers.items():
            if nid != src_node:
                await q.put({"from": src_node, "msg": message, "ts": datetime.datetime.utcnow().isoformat()})
        LOG.debug(f"transport: {src_node} published to {len(self.subscribers)-1} nodes")

class AsyncDeltaNode:
    """A single async ∆ node with its own DeltaOS orchestrator"""
    def __init__(self, node_id: str, intent: Dict[str, Any], transport: InMemoryTransport):
        self.node_id = node_id
        self.intent = intent
        self.transport = transport
        self.system = DeltaOS(intent=intent)
        self.queue: Optional[asyncio.Queue] = None
        self.running = False

    async def start(self, raw_env: Dict[str, Any]):
        self.queue = await self.transport.register(self.node_id)
        self.system.init_node(self.node_id, raw_env)
        self.running = True
        LOG.info(f"node {self.node_id} started")

    async def stop(self):
        self.running = False
        if self.queue:
            await self.transport.unregister(self.node_id)
        LOG.info(f"node {self.node_id} stopped")

    async def run_cycle_async(self, input_data: Dict[str, Any], raw_env: Dict[str, Any]):
        record, feedback = await asyncio.get_event_loop().run_in_executor(
            None, lambda: self.system.run_cycle(input_data, raw_env, node_id=self.node_id))
        await self.transport.publish(self.node_id, {"context": record["context"], "delta": record["delta_info"]})
        return record, feedback

    async def listen(self):
        if not self.queue:
            raise RuntimeError("node not started")
        while self.running:
            try:
                msg = await asyncio.wait_for(self.queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            peer = msg.get("from")
            ctx = msg.get("msg", {}).get("context")
            if ctx:
                try:
                    self.system.transmission.register_node(peer, type("Sig", (), {"summary": lambda self=None, c=ctx: c})())
                    LOG.info(f"node {self.node_id} received context from {peer}")
                except Exception:
                    LOG.debug(f"node {self.node_id} failed to register peer context")

async def demo_async_deltanet(cycles: int = 6):
    """Demo: Run three nodes in parallel with context synchronization"""
    transport = InMemoryTransport()
    nodes = [
        AsyncDeltaNode("healing", {"priority": "restoration"}, transport),
        AsyncDeltaNode("heritage", {"priority": "preservation"}, transport),
        AsyncDeltaNode("finance", {"priority": "ethical_growth"}, transport),
    ]

    # Start nodes
    for n in nodes:
        await n.start({"risk_tolerance": 0.3})

    # Start listeners
    listeners = [asyncio.create_task(n.listen()) for n in nodes]

    # Run cycles
    for i in range(cycles):
        tasks = []
        for n in nodes:
            market_index = 1000.0 + random.normalvariate(0, 5) + (5 if i == cycles // 2 else 0)
            input_data = {"market_index": round(market_index, 6)}
            raw_env = {"risk_tolerance": 0.3, "domain": n.node_id}
            tasks.append(asyncio.create_task(n.run_cycle_async(input_data, raw_env)))
        
        results = await asyncio.gather(*tasks)
        LOG.info(f"Completed cycle {i+1}/{cycles}")
        for idx, (record, feedback) in enumerate(results):
            LOG.info(f"Node {nodes[idx].node_id} - intent_score={record.get('intent_score')} plan_conf={record.get('plan', {}).get('confidence')}")
        
        await asyncio.sleep(0.5)

    # Cleanup
    for n in nodes:
        await n.stop()
    for l in listeners:
        l.cancel()
    LOG.info("demo_async_deltanet complete")

if __name__ == "__main__":
    asyncio.run(demo_async_deltanet(cycles=6))
