from datetime import datetime, timezone
import os
import logging
from typing import Any, Dict
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Δ Delta Operating System API",
    description="Consciousness Conductor | Impact Protocol Engine",
    version="1.0.0",
)

# CORS must be explicitly configured in production.  A wildcard origin cannot
# safely be combined with credentialed requests.
cors_origins = [
    origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()
]

REQUEST_COUNT = Counter(
    "delta_os_http_requests_total", "HTTP requests served", ["method", "path", "status"]
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    request.state.request_id = request_id
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Unhandled request error", extra={"request_id": request_id})
        response = JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "request_id": request_id},
        )
    response.headers["X-Request-ID"] = request_id
    REQUEST_COUNT.labels(request.method, request.url.path, str(response.status_code)).inc()
    return response


# Cross-origin access is disabled by default; configure CORS_ORIGINS when a
# browser client needs to make credentialed cross-origin requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=bool(cors_origins),
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)


@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "message": "Δ Delta OS - Infininoniac Edition",
        "status": "operational",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "api",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """Readiness for the API process; dependency checks belong to their clients."""
    return {"status": "ready", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/v1/nodes")
async def get_nodes() -> Dict[str, Any]:
    return {
        "nodes": [
            {"id": "node-1", "status": "active", "domain": "health"},
            {"id": "node-2", "status": "active", "domain": "environment"},
            {"id": "node-3", "status": "active", "domain": "finance"},
        ],
        "version": "v1",
        "total_nodes": 3,
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
        "🎨 Heritage & Culture",
    ]
    return {"domains": domains, "count": len(domains)}


@app.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Railway-specific startup
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    logger.info(f"🚀 Starting Delta OS on port {port}")
    logger.info(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'development')}")

    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=False, access_log=True)
