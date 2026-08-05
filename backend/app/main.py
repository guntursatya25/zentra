import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config import settings
from app.middleware.error_handler import register_error_handlers
from app.middleware.logging import RequestLoggingMiddleware
from app.services.rate_limit import RateLimitMiddleware
from app.routers import admin, auth, categories, chat, documents, health, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.upload_dir, exist_ok=True)
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    lifespan=lifespan,
)

# ── Middleware (order: outermost first) ──

# Production: restrict to known hosts
allowed_hosts = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[h.strip() for h in allowed_hosts.split(",")],
)

# CORS — restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Rate limiting (innermost middleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)

# Request logging
app.add_middleware(RequestLoggingMiddleware)

# ── Global error handler ──
register_error_handlers(app)

# ── Routers ──
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(admin.router)
