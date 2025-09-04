import redis
import logging
from typing import Optional
from config.settings import settings

logger = logging.getLogger(__name__)

class RedisManager:
    """Redis connection manager using configuration settings."""
    
    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._connected: bool = False
        self._config = {
            'host': settings.REDIS_HOST,
            'port': settings.REDIS_PORT,
            'password': settings.REDIS_PASSWORD or None,
            'db': settings.REDIS_DB,
            'decode_responses': True,
            'socket_connect_timeout': settings.REDIS_CONNECTION_TIMEOUT,
            'socket_timeout': settings.REDIS_SOCKET_TIMEOUT,
            'retry_on_timeout': settings.REDIS_RETRY_ON_TIMEOUT,
            'health_check_interval': settings.REDIS_HEALTH_CHECK_INTERVAL,
            'max_connections': settings.REDIS_MAX_CONNECTIONS
        }
    
    def connect(self) -> bool:
        """Establish connection to Redis using configuration."""
        try:
            # Use URL if provided, otherwise use individual parameters
            if settings.REDIS_URL:
                self._redis = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=settings.REDIS_CONNECTION_TIMEOUT,
                    socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                    retry_on_timeout=settings.REDIS_RETRY_ON_TIMEOUT,
                    health_check_interval=settings.REDIS_HEALTH_CHECK_INTERVAL,
                    max_connections=settings.REDIS_MAX_CONNECTIONS
                )
            else:
                self._redis = redis.Redis(**self._config)
            
            # Test connection
            self._redis.ping()
            self._connected = True
            logger.info(f"Successfully connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            return True
            
        except redis.RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._connected = False
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to Redis: {e}")
            self._connected = False
            return False
    
    def get_client(self) -> Optional[redis.Redis]:
        """Get Redis client, reconnecting if necessary."""
        if not self._connected or not self._redis:
            if not self.connect():
                return None
        
        try:
            # Test if connection is still alive
            self._redis.ping()
            return self._redis
        except redis.RedisError:
            logger.warning("Redis connection lost, attempting to reconnect")
            if self.connect():
                return self._redis
            return None
    
    def is_connected(self) -> bool:
        """Check if Redis is connected and available."""
        client = self.get_client()
        if not client:
            return False
        
        try:
            client.ping()
            return True
        except redis.RedisError:
            return False
    
    def get_info(self) -> dict:
        """Get Redis configuration and connection info."""
        return {
            "host": settings.REDIS_HOST,
            "port": settings.REDIS_PORT,
            "db": settings.REDIS_DB,
            "connected": self._connected,
            "url": settings.REDIS_URL.replace(settings.REDIS_PASSWORD, "***") if settings.REDIS_PASSWORD else settings.REDIS_URL,
            "connection_timeout": settings.REDIS_CONNECTION_TIMEOUT,
            "socket_timeout": settings.REDIS_SOCKET_TIMEOUT,
            "max_connections": settings.REDIS_MAX_CONNECTIONS
        }
    
    def close(self):
        """Close Redis connection."""
        if self._redis:
            try:
                self._redis.close()
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
            finally:
                self._redis = None
                self._connected = False

# Global Redis manager instance
redis_manager = RedisManager()