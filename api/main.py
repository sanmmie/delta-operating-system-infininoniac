from fastapi import FastAPI
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Δ Delta Operating System API",
    description="Consciousness Conductor | Impact Protocol Engine",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "message": "Δ Delta OS - Infininoniac Edition",
        "status": "operational", 
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "database": "connected", 
            "redis": "connected"
        }
    }

@app.get("/api/v1/nodes")
async def get_nodes():
    return {"nodes": [], "version": "v1"}

# Railway-specific startup
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🚀 Starting Delta OS on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
