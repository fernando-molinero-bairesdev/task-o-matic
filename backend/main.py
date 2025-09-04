from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.task_router import router as task_router
from routers.user_router import router as user_router
from routers.auth_router import router as auth_router
from services.redis_service import redis_manager
from config.settings import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url=settings.API_DOCS_URL,
    redoc_url=settings.API_REDOC_URL
)

# Add CORS middleware with explicit configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Cache-Control",
        "Pragma",
        "Origin",
        "Referer",
        "User-Agent"
    ],
    expose_headers=[
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
        "X-Process-Time"
    ]
)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    if settings.RATE_LIMIT_ENABLED:
        success = redis_manager.connect()
        if success:
            logger.info("Redis connected successfully for rate limiting")
        else:
            logger.warning("Failed to connect to Redis - rate limiting may not work properly")
    else:
        logger.info("Rate limiting disabled")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    redis_manager.close()
    logger.info("Application shutdown complete")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Task-O-Matic API",
        "version": settings.API_VERSION,
        "rate_limiting": settings.RATE_LIMIT_ENABLED
    }

@app.get("/health")
async def health_check():
    """Health check endpoint with Redis status."""
    return {
        "status": "healthy",
        "redis_connected": redis_manager.is_connected(),
        "rate_limiting_enabled": settings.RATE_LIMIT_ENABLED,
        "redis_info": redis_manager.get_info() if redis_manager.is_connected() else None
    }

# Include routers with prefixes - Make sure task router is included!
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(task_router, prefix="/tasks", tags=["Tasks"])
app.include_router(user_router, prefix="/users", tags=["Users"])