from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import api_router
from app.core.config import settings
from app.core.rate_limit import RateLimiter

app = FastAPI(title=settings.app_name)
app.include_router(api_router)

origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rate_limiter = RateLimiter(settings.rate_limit_per_minute)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if settings.enable_rate_limit:
        client_ip = request.client.host if request.client else "unknown"
        if not rate_limiter.allow(client_ip):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded"},
            )
    return await call_next(request)
