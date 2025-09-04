import time
import hashlib
from typing import Optional, Tuple
from fastapi import Request
from services.redis_service import redis_manager
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiting service using Redis."""
    
    def __init__(self):
        self.enabled = settings.RATE_LIMIT_ENABLED
        self.prefix = settings.RATE_LIMIT_STORAGE_PREFIX
        self.exempt_ips = set(settings.RATE_LIMIT_EXEMPT_IPS)
    
    def _get_client_identifier(self, request: Request) -> str:
        """Generate a unique identifier for the client."""
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Try to get user ID from request state (set by auth middleware)
        user_id = getattr(request.state, 'user_id', None)
        
        if user_id:
            # Use user ID for authenticated requests
            return f"user:{user_id}"
        else:
            # Use IP for unauthenticated requests
            return f"ip:{client_ip}"
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        # Check for forwarded headers first (proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"
    
    def _is_exempt(self, request: Request) -> bool:
        """Check if the client IP is exempt from rate limiting."""
        client_ip = self._get_client_ip(request)
        return client_ip in self.exempt_ips
    
    def _get_rate_limit_key(self, identifier: str, limit_type: str) -> str:
        """Generate Redis key for rate limiting."""
        current_window = int(time.time() // settings.RATE_LIMITS[limit_type]["window"])
        key_data = f"{identifier}:{limit_type}:{current_window}"
        # Use hash to keep keys short and avoid special characters
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{self.prefix}:{key_hash}"
    
    async def check_rate_limit(
        self, 
        request: Request, 
        limit_type: str = "global"
    ) -> Tuple[bool, Optional[str], int, int]:
        """
        Check if request is within rate limits.
        
        Returns:
            (is_allowed, error_message, remaining_requests, reset_time)
        """
        if not self.enabled:
            return True, None, 999, 0
        
        if self._is_exempt(request):
            return True, None, 999, 0
        
        if limit_type not in settings.RATE_LIMITS:
            logger.warning(f"Unknown rate limit type: {limit_type}")
            limit_type = "global"
        
        limit_config = settings.RATE_LIMITS[limit_type]
        max_requests = limit_config["requests"]
        window_seconds = limit_config["window"]
        error_message = limit_config["message"]
        
        redis_client = redis_manager.get_client()
        if not redis_client:
            # If Redis is unavailable, allow request but log warning
            logger.warning("Redis unavailable, allowing request")
            return True, None, max_requests, 0
        
        try:
            identifier = self._get_client_identifier(request)
            rate_limit_key = self._get_rate_limit_key(identifier, limit_type)
            
            # Get current count
            current_count = redis_client.get(rate_limit_key)
            current_count = int(current_count) if current_count else 0
            
            if current_count >= max_requests:
                # Rate limit exceeded
                ttl = redis_client.ttl(rate_limit_key)
                reset_time = int(time.time() + ttl) if ttl > 0 else int(time.time() + window_seconds)
                return False, error_message, 0, reset_time
            
            # Increment counter
            pipe = redis_client.pipeline()
            pipe.incr(rate_limit_key, 1)
            pipe.expire(rate_limit_key, window_seconds)
            pipe.execute()
            
            remaining = max_requests - (current_count + 1)
            reset_time = int(time.time() + window_seconds)
            
            return True, None, remaining, reset_time
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # On error, allow the request
            return True, None, max_requests, 0

# Global rate limiter instance
rate_limiter = RateLimiter()