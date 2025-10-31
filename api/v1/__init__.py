# api/v1/__init__.py
from fastapi import APIRouter

v1_router = APIRouter(prefix="/api/v1")

@v1_router.get("/nodes")
async def get_nodes():
    return {"version": "v1", "nodes": []}

# In main.py
app.include_router(v1_router, prefix="/api/v1")
