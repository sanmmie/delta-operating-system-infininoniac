"""
Delta Operating System - Consciousness Conductor
Phase III: Async Multi-Node Coordination

"""

import asyncio
import datetime
import logging
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# Minimal fallback definitions
@dataclass
class TransformationPlan:
    actions: List[Dict[str, Any]] = field(default_factory=list)
    rationale: str = ""
    confidence: float = 0.0


class DeltaEngine:
    def __init__(self, sensitivity: float = 0.02):
        self.sensitivity = sensitivity

    def compute_delta(self, input_data, history):
        if history:
            prev = history[-1].get("market_index", 0.0)
        else:
            prev = input_data.get("market_index", 0.0)
        curr = input_data.get("market_index", prev)
        delta = curr - prev
        denom = max(abs(prev), 1.0)
        normalized = delta / denom
        return {
            "delta": delta,
            "normalized": normalized,
            "prev": prev,
            "curr": curr
        }

    def generate_transformation_map(self, delta_info, context):
        d = delta_info["normalized"]
        actions = []
        rationale = ""
        confidence = min(0.95, max(0.05, abs(d)))
        
        if d > self.sensitivity:
            actions.append({
                "type": "increase_allocation",
                "target": "equities",
                "magnitude": min(0.2, d)
            })
            rationale = "Market trending up; opportunistic increase."
        elif d < -self.sensitivity:
            actions.append({
                "type": "decrease_allocation", 
                "target": "equities",
                "magnitude": min(0.2, -d)
            })
            rationale = "Market trending down; defensive posture."
        else:
            actions.append({
                "type": "hold",
                "target": "portfolio", 
                "magnitude": 0.0
            })
            rationale = "No strong trend; maintain position."
        
        if isinstance(context, dict):
            risk = float(context.get("risk_tolerance", 0.5))
        else:
            risk = 0.5
            
        for action in actions:
            action["adjusted_magnitude"] = action.get("magnitude", 0.0) * (1.0 - risk)
            
        return TransformationPlan(
            actions=actions,
            rationale=rationale,
            confidence=confidence
        )


class ContextCompiler:
    def compile(self, raw_env):
        timestamp = datetime.datetime.utcnow()
        environment = dict(raw_env)
        environment.setdefault("risk_tolerance", 0.5)
        environment.setdefault("ethical_constraints", {})
        
        return CompiledContext(environment, timestamp)


class CompiledContext:
    def __init__(self, environment, timestamp):
        self.env = environment
        self.timestamp = timestamp
    
    def summary(self):
        result = dict(self.env)
        result["ts"] = self.timestamp.isoformat()
        return result


class Modules:
    def __init__(self):
        self.history = []
    
    def observe(self, data):
        self.history.append(dict(data))
        return {"pattern_map": data}
    
    def reflect(self, record):
        return {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "success": False,
            "notes": "fallback"
        }


class Transmission:
    def __init__(self):
        self.nodes = {}
    
    def register_node(self, node_id, signature):
        self.nodes[node_id] = signature.summary()
    
    def sync_context(self, node_a, node_b):
        context_a = self.nodes.get(node_a, {})
        context_b = self.nodes.get(node_b, {})
        return {**context_a, **context_b}


class DeltaOS:
    def __init__(self, intent):
        self.kernel_delta = DeltaEngine()
        self.compiler = ContextCompiler()
        self.integrator = None
        self.modules = Modules()
        self.transmission = Transmission()
        self.intent = intent
        self.cycle_log = []

    def init_node(self, node_id, raw_env):
        context = self.compiler.compile(raw_env)
        self.transmission.register_node(node_id, context)
        return context

    def run_cycle(self, input_data, raw_env, node_id=None):
        self.modules.observe(input_data)
        context = self.compiler.compile(raw_env)
        
        history_slice = self.modules.history[:-1]
        delta_info = self.kernel_delta.compute_delta(input_data, history_slice)
        
        plan = self.kernel_delta.generate_transformation_map(delta_info, context)
        plan_dict = {
            "actions": plan.actions,
            "rationale": plan.rationale,
            "confidence": plan.confidence
        }
        
        cycle_record = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "input": input_data,
            "context": context.summary(),
            "delta_info": delta_info,
            "plan": plan_dict,
            "intent_score": 0.5
        }
        
        feedback = self.modules.reflect(cycle_record)
        
        self.cycle_log.append({
            "cycle": len(self.cycle_log) + 1,
            "record": cycle_record,
            "feedback": feedback
        })
        
        if node_id:
            self.transmission.register_node(node_id, context)
            
        return cycle_record, feedback


# Setup logging
logger = logging.getLogger("delta_net_async")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class InMemoryTransport:
    def __init__(self):
        self.subscribers = {}

    async def register(self, node_id):
        queue = asyncio.Queue()
        self.subscribers[node_id] = queue
        logger.debug("Transport: registered %s", node_id)
        return queue

    async def unregister(self, node_id):
        if node_id in self.subscribers:
            del self.subscribers[node_id]
        logger.debug("Transport: unregistered %s", node_id)

    async def publish(self, source_node, message):
        subscribers_count = 0
        for node_id, queue in self.subscribers.items():
            if node_id != source_node:
                await queue.put({
                    "from": source_node,
                    "msg": message,
                    "ts": datetime.datetime.utcnow().isoformat()
                })
                subscribers_count += 1
        logger.debug("Transport: %s published to %s nodes", source_node, subscribers_count)


class AsyncDeltaNode:
    def __init__(self, node_id, intent, transport):
        self.node_id = node_id
        self.intent = intent
        self.transport = transport
        self.system = DeltaOS(intent)
        self.queue = None
        self.running = False

    async def start(self, raw_env):
        self.queue = await self.transport.register(self.node_id)
        self.system.init_node(self.node_id, raw_env)
        self.running = True
        logger.info("Node %s started", self.node_id)

    async def stop(self):
        self.running = False
        if self.queue:
            await self.transport.unregister(self.node_id)
        logger.info("Node %s stopped", self.node_id)

    async def run_cycle_async(self, input_data, raw_env):
        def run_sync():
            return self.system.run_cycle(input_data, raw_env, self.node_id)
            
        record, feedback = await asyncio.get_event_loop().run_in_executor(None, run_sync)
        
        await self.transport.publish(self.node_id, {
            "context": record["context"],
            "delta": record["delta_info"]
        })
        
        return record, feedback

    async def listen(self):
        if not self.queue:
            raise RuntimeError("Node not started")
            
        while self.running:
            try:
                message = await asyncio.wait_for(self.queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
                
            peer = message.get("from")
            context_data = message.get("msg", {}).get("context")
            
            if context_data:
                class PeerSignature:
                    @staticmethod
                    def summary():
                        return context_data
                        
                try:
                    self.system.transmission.register_node(peer, PeerSignature())
                    logger.info("Node %s received context from %s", self.node_id, peer)
                except Exception:
                    logger.debug("Node %s failed to register peer context", self.node_id)


async def demo_async_deltanet(cycles=6):
    transport = InMemoryTransport()
    
    nodes = [
        AsyncDeltaNode("healing", {"priority": "restoration"}, transport),
        AsyncDeltaNode("heritage", {"priority": "preservation"}, transport),
        AsyncDeltaNode("finance", {"priority": "ethical_growth"}, transport),
    ]

    # Start nodes
    for node in nodes:
        await node.start({"risk_tolerance": 0.3})

    # Start listeners
    listeners = []
    for node in nodes:
        task = asyncio.create_task(node.listen())
        listeners.append(task)

    # Run cycles
    for cycle_num in range(cycles):
        tasks = []
        for node in nodes:
            base_value = 1000.0
            random_change = random.normalvariate(0, 5)
            if cycle_num == cycles // 2:
                random_change += 5
            market_index = base_value + random_change
            input_data = {"market_index": round(market_index, 6)}
            raw_env = {"risk_tolerance": 0.3, "domain": node.node_id}
            task = asyncio.create_task(node.run_cycle_async(input_data, raw_env))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        logger.info("Completed cycle %s/%s", cycle_num + 1, cycles)
        
        for index, (record, feedback) in enumerate(results):
            logger.info(
                "Node %s - intent_score=%s plan_conf=%s",
                nodes[index].node_id,
                record.get('intent_score'),
                record.get('plan', {}).get('confidence')
            )
        
        await asyncio.sleep(0.5)

    # Cleanup
    for node in nodes:
        await node.stop()
        
    for listener_task in listeners:
        listener_task.cancel()
        
    logger.info("Demo async deltanet complete")


if __name__ == "__main__":
    asyncio.run(demo_async_deltanet(cycles=6))
