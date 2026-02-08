"""
Health check endpoints for container orchestration.

Provides separate liveness and readiness probes for proper
Kubernetes/Docker health monitoring and load balancing.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as aioredis
from app.db.session import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/health/live")
async def liveness():
    """
    Liveness probe - Is the process running?
    
    Returns 200 if the application process is alive.
    Kubernetes uses this to know when to restart a container.
    
    This endpoint should be lightweight and not check external dependencies.
    """
    return {"status": "alive", "service": "easeemail-api"}


@router.get("/health/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    """
    Readiness probe - Can the application serve traffic?
    
    Checks database and redis connectivity.
    Kubernetes uses this to know when to add pod to load balancer.
    
    Returns:
        200: Service is ready to handle requests
        503: Service is alive but not ready (dependencies unavailable)
    """
    errors = []
    
    # Check PostgreSQL connectivity
    try:
        result = await db.execute(text("SELECT 1"))
        await db.commit()
    except Exception as e:
        errors.append(f"PostgreSQL: {str(e)[:100]}")
    
    # Check Redis connectivity
    try:
        r = aioredis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            socket_timeout=3,
            decode_responses=True
        )
        await r.ping()
        await r.aclose()
    except Exception as e:
        errors.append(f"Redis: {str(e)[:100]}")
    
    if errors:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "errors": errors,
                "message": "Service dependencies are unavailable"
            }
        )
    
    return {
        "status": "ready",
        "database": "ok",
        "redis": "ok",
        "service": "easeemail-api"
    }


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    """
    Combined health check for backwards compatibility.
    
    This endpoint is equivalent to /health/ready and checks all dependencies.
    """
    return await readiness(db)
