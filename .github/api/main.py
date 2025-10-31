from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Δ Delta Operating System API",
    description="Consciousness Conductor | Impact Protocol Engine",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "message": "Δ Delta OS - Infininoniac Edition",
        "status": "operational",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "database": "available",
            "redis": "available"
        },
        "timestamp": "2024-01-01T00:00:00Z"  # You can make this dynamic later
    }

@app.get("/api/v1/nodes")
async def get_nodes() -> Dict[str, Any]:
    return {
        "nodes": [
            {"id": "node-1", "status": "active", "domain": "health"},
            {"id": "node-2", "status": "active", "domain": "environment"},
            {"id": "node-3", "status": "active", "domain": "finance"}
        ],
        "version": "v1",
        "total_nodes": 3
    }

@app.get("/api/v1/domains")
async def get_domains() -> Dict[str, Any]:
    domains = [
        "🩺 Healing & Health",
        "🌱 Climate & Environment", 
        "💰 Finance & Economics",
        "📚 Education & Knowledge",
        "🏛️ Governance & Leadership",
        "⚡ Energy & Resources",
        "🌾 Agriculture & Food",
        "💧 Water & Sanitation",
        "🔗 Connectivity & Digital Access",
        "🎨 Heritage & Culture"
    ]
    return {"domains": domains, "count": len(domains)}

@app.get("/metrics")
async def metrics() -> Dict[str, Any]:
    return {
        "active_connections": 0,
        "memory_usage": "0MB",
        "uptime": "0s"
    }

# Railway-specific startup
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🚀 Starting Delta OS on port {port}")
    logger.info(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        access_log=True
    )
