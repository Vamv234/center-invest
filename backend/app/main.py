from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.database import AsyncSessionLocal, ensure_database_schema
from app.core.redis import close_redis
from app.services.scenario_gameplay import scenario_gameplay_service

WEB_ROOT = Path(__file__).resolve().parent / "web"
UI_FILE = WEB_ROOT / "index.html"


@asynccontextmanager
async def lifespan(_: FastAPI):
    await ensure_database_schema()
    async with AsyncSessionLocal() as db:
        await scenario_gameplay_service.seed_scenarios(db, seed_path=settings.scenario_seed_path)
    yield
    await close_redis()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/ui", status_code=307)


@app.get("/ui", include_in_schema=False)
async def ui() -> FileResponse:
    return FileResponse(UI_FILE)


@app.get("/api-info", tags=["system"])
async def api_info() -> dict[str, str]:
    return {"message": settings.app_name}


@app.get("/favicon.ico", include_in_schema=False, status_code=204)
async def favicon() -> Response:
    return Response(status_code=204)


@app.get("/apple-touch-icon.png", include_in_schema=False, status_code=204)
async def apple_touch_icon() -> Response:
    return Response(status_code=204)


@app.get("/apple-touch-icon-precomposed.png", include_in_schema=False, status_code=204)
async def apple_touch_icon_precomposed() -> Response:
    return Response(status_code=204)
