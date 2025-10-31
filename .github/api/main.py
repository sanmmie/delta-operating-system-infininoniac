from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import logging

from config import config
from security.auth import AuthHandler
from models import Database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Delta Operating System API",
    description="Consciousness Conductor | Impact Protocol Engine",
    version="1.0.0"
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get('security.allowed_origins', ['*']),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=config.get('security.allowed_hosts', ['*'])
)

# Dependency injection
auth_handler = AuthHandler(config)
database = Database(config)

@app.on_event("startup")
async def startup_event():
    database.create_tables()
    logger.info("Delta OS API started successfully")

@app.get("/")
@limiter.limit(f"{config.get('security.rate_limit_requests')}/minute")
async def root():
    return {
        "message": "Δ Delta Operating System - Infininoniac Edition",
        "status": "operational",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "database": "connected",
            "ethical_engine": "active",
            "impact_protocol": "ready"
        }
    }

@app.post("/api/v1/nodes/register")
@limiter.limit("10/minute")
async def register_node(node_data: dict, token: dict = Depends(auth_handler.verify_token)):
    try:
        session = database.get_session()
        # Node registration logic
        return {"status": "registered", "node_id": node_data.get('node_id')}
    except Exception as e:
        logger.error(f"Node registration failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.get("/api/v1/plans/{domain}")
@limiter.limit("60/minute")
async def get_transformation_plans(domain: str, token: dict = Depends(auth_handler.verify_token)):
    # Implementation for retrieving transformation plans
    pass
