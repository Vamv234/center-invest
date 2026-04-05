from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.database import check_db_connection
from app.core.redis import check_redis_connection

router = APIRouter()


@router.get("/live")
async def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready() -> JSONResponse:
    database_ok = await check_db_connection()
    redis_ok = await check_redis_connection()
    healthy = database_ok and redis_ok
    return JSONResponse(
        status_code=200 if healthy else 503,
        content={
            "status": "ok" if healthy else "degraded",
            "services": {
                "database": database_ok,
                "redis": redis_ok,
            },
        },
    )
