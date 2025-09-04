import time
from fastapi import Request, HTTPException, Depends
from services.rate_limiter import rate_limiter
import logging

logger = logging.getLogger(__name__)

async def check_rate_limit_dependency(
    request: Request,
    limit_type: str = "global"
):
    """Dependency to check rate limits for specific endpoints."""
    is_allowed, error_message, remaining, reset_time = await rate_limiter.check_rate_limit(
        request, limit_type
    )
    
    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": error_message,
                "limit_type": limit_type,
                "retry_after": reset_time - int(time.time())
            },
            headers={
                "Retry-After": str(reset_time - int(time.time()))
            }
        )
    
    return {
        "remaining": remaining,
        "reset_time": reset_time,
        "limit_type": limit_type
    }

# Specific rate limit dependencies
async def check_auth_rate_limit(request: Request):
    """Rate limit dependency for authentication endpoints."""
    return await check_rate_limit_dependency(request, "auth")

async def check_tasks_read_rate_limit(request: Request):
    """Rate limit dependency for task read operations."""
    return await check_rate_limit_dependency(request, "tasks_read")

async def check_tasks_write_rate_limit(request: Request):
    """Rate limit dependency for task write operations."""
    return await check_rate_limit_dependency(request, "tasks_write")

async def check_tasks_delete_rate_limit(request: Request):
    """Rate limit dependency for task delete operations."""
    return await check_rate_limit_dependency(request, "tasks_delete")

async def check_global_rate_limit(request: Request):
    """Rate limit dependency for global operations."""
    return await check_rate_limit_dependency(request, "global")