import os
import toml
from typing import Dict, Any, Optional, List
from pydantic import field_validator, ConfigDict
from pydantic_settings import BaseSettings
from pathlib import Path

class ConfigSettings(BaseSettings):
    """Configuration settings loaded from TOML file and environment variables."""
    
    # Add model configuration to allow extra fields
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # This allows extra fields to be ignored instead of raising errors
        validate_default=True
    )
    
    # Database settings
    DATABASE_URL: str = "postgresql://taskomatic:taskomatic@db:5432/taskomatic"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600
    
    # PostgreSQL specific settings (to handle the environment variables)
    POSTGRES_USER: str = "taskomatic"
    POSTGRES_PASSWORD: str = "taskomatic"
    POSTGRES_DB: str = "taskomatic"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: str = "5432"
    
    # Redis settings
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    REDIS_URL: str = ""
    REDIS_CONNECTION_TIMEOUT: int = 5
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_RETRY_ON_TIMEOUT: bool = True
    REDIS_HEALTH_CHECK_INTERVAL: int = 30
    REDIS_MAX_CONNECTIONS: int = 10
    
    # Rate limiting settings
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_STORAGE_PREFIX: str = "rate_limit"
    RATE_LIMIT_EXEMPT_IPS: List[str] = ["127.0.0.1", "localhost", "::1"]
    
    # Rate limit configurations
    RATE_LIMITS: Dict[str, Dict[str, Any]] = {
        "auth": {"requests": 10, "window": 60, "message": "Too many authentication requests. Please try again later."},
        "tasks_read": {"requests": 100, "window": 60, "message": "Too many read requests. Please slow down."},
        "tasks_write": {"requests": 30, "window": 60, "message": "Too many write requests. Please slow down."},
        "tasks_delete": {"requests": 10, "window": 60, "message": "Too many delete requests. Please slow down."},
        "global": {"requests": 200, "window": 60, "message": "Too many requests. Please slow down."}
    }
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS settings
    CORS_ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOWED_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"]
    CORS_ALLOWED_HEADERS: List[str] = [
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
    ]
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "logs/app.log"
    LOG_MAX_BYTES: int = 10485760
    LOG_BACKUP_COUNT: int = 5
    
    # Cache settings
    CACHE_DEFAULT_TTL: int = 300
    CACHE_TASK_LIST_TTL: int = 60
    CACHE_USER_INFO_TTL: int = 900
    
    # API settings
    API_TITLE: str = "Task-O-Matic API"
    API_DESCRIPTION: str = "A comprehensive task management system"
    API_VERSION: str = "1.0.0"
    API_DOCS_URL: str = "/docs"
    API_REDOC_URL: str = "/redoc"
    
    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def build_redis_url(cls, v, info):
        """Build Redis URL from components if not provided."""
        if v:
            return v
        
        # Get values from the validation context
        values = info.data if info.data else {}
        
        host = values.get("REDIS_HOST", "redis")
        port = values.get("REDIS_PORT", 6379)
        password = values.get("REDIS_PASSWORD", "")
        db = values.get("REDIS_DB", 0)
        
        if password:
            return f"redis://:{password}@{host}:{port}/{db}"
        else:
            return f"redis://{host}:{port}/{db}"
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def build_database_url(cls, v, info):
        """Build database URL from PostgreSQL components if not provided."""
        if v and v != "postgresql://taskomatic:taskomatic@db:5432/taskomatic":
            return v
        
        # Get values from the validation context
        values = info.data if info.data else {}
        
        user = values.get("POSTGRES_USER", "taskomatic")
        password = values.get("POSTGRES_PASSWORD", "taskomatic")
        host = values.get("POSTGRES_HOST", "db")
        port = values.get("POSTGRES_PORT", "5432")
        db = values.get("POSTGRES_DB", "taskomatic")
        
        return f"postgresql://{user}:{password}@{host}:{port}/{db}"

def load_config_from_toml(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from TOML file."""
    if config_path is None:
        # Look for config.toml in current directory or backend directory
        possible_paths = [
            Path("config.toml"),
            Path("backend/config.toml"),
            Path("../config.toml"),
            Path.cwd() / "config.toml"
        ]
        
        for path in possible_paths:
            if path.exists():
                config_path = str(path)
                break
    
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r') as f:
                config_data = toml.load(f)
            return config_data
        except Exception as e:
            print(f"Warning: Failed to load TOML config from {config_path}: {e}")
            return {}
    else:
        print("Warning: No config.toml file found, using defaults and environment variables")
        return {}

def merge_toml_with_settings(toml_config: Dict[str, Any], settings: ConfigSettings) -> ConfigSettings:
    """Merge TOML configuration with settings object."""
    
    # Database settings
    if "database" in toml_config:
        db_config = toml_config["database"]
        settings.DATABASE_URL = db_config.get("url", settings.DATABASE_URL)
        settings.DATABASE_POOL_SIZE = db_config.get("pool_size", settings.DATABASE_POOL_SIZE)
        settings.DATABASE_MAX_OVERFLOW = db_config.get("max_overflow", settings.DATABASE_MAX_OVERFLOW)
        settings.DATABASE_POOL_TIMEOUT = db_config.get("pool_timeout", settings.DATABASE_POOL_TIMEOUT)
        settings.DATABASE_POOL_RECYCLE = db_config.get("pool_recycle", settings.DATABASE_POOL_RECYCLE)
    
    # Redis settings
    if "redis" in toml_config:
        redis_config = toml_config["redis"]
        settings.REDIS_HOST = redis_config.get("host", settings.REDIS_HOST)
        settings.REDIS_PORT = redis_config.get("port", settings.REDIS_PORT)
        settings.REDIS_PASSWORD = redis_config.get("password", settings.REDIS_PASSWORD)
        settings.REDIS_DB = redis_config.get("db", settings.REDIS_DB)
        settings.REDIS_URL = redis_config.get("url", settings.REDIS_URL)
        settings.REDIS_CONNECTION_TIMEOUT = redis_config.get("connection_timeout", settings.REDIS_CONNECTION_TIMEOUT)
        settings.REDIS_SOCKET_TIMEOUT = redis_config.get("socket_timeout", settings.REDIS_SOCKET_TIMEOUT)
        settings.REDIS_RETRY_ON_TIMEOUT = redis_config.get("retry_on_timeout", settings.REDIS_RETRY_ON_TIMEOUT)
        settings.REDIS_HEALTH_CHECK_INTERVAL = redis_config.get("health_check_interval", settings.REDIS_HEALTH_CHECK_INTERVAL)
        settings.REDIS_MAX_CONNECTIONS = redis_config.get("max_connections", settings.REDIS_MAX_CONNECTIONS)
    
    # Rate limiting settings
    if "rate_limiting" in toml_config:
        rl_config = toml_config["rate_limiting"]
        settings.RATE_LIMIT_ENABLED = rl_config.get("enabled", settings.RATE_LIMIT_ENABLED)
        settings.RATE_LIMIT_STORAGE_PREFIX = rl_config.get("storage_prefix", settings.RATE_LIMIT_STORAGE_PREFIX)
        settings.RATE_LIMIT_EXEMPT_IPS = rl_config.get("exempt_ips", settings.RATE_LIMIT_EXEMPT_IPS)
        
        # Rate limit configurations
        if "limits" in rl_config:
            limits_config = rl_config["limits"]
            for limit_type, limit_settings in limits_config.items():
                if limit_type in settings.RATE_LIMITS:
                    settings.RATE_LIMITS[limit_type].update(limit_settings)
                else:
                    settings.RATE_LIMITS[limit_type] = limit_settings
    
    # Security settings
    if "security" in toml_config:
        security_config = toml_config["security"]
        settings.SECRET_KEY = security_config.get("secret_key", settings.SECRET_KEY)
        settings.ALGORITHM = security_config.get("algorithm", settings.ALGORITHM)
        settings.ACCESS_TOKEN_EXPIRE_MINUTES = security_config.get("access_token_expire_minutes", settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        settings.REFRESH_TOKEN_EXPIRE_DAYS = security_config.get("refresh_token_expire_days", settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    # CORS settings
    if "cors" in toml_config:
        cors_config = toml_config["cors"]
        settings.CORS_ALLOWED_ORIGINS = cors_config.get("allowed_origins", settings.CORS_ALLOWED_ORIGINS)
        settings.CORS_ALLOW_CREDENTIALS = cors_config.get("allow_credentials", settings.CORS_ALLOW_CREDENTIALS)
        settings.CORS_ALLOWED_METHODS = cors_config.get("allowed_methods", settings.CORS_ALLOWED_METHODS)
        settings.CORS_ALLOWED_HEADERS = cors_config.get("allowed_headers", settings.CORS_ALLOWED_HEADERS)
    
    # Logging settings
    if "logging" in toml_config:
        logging_config = toml_config["logging"]
        settings.LOG_LEVEL = logging_config.get("level", settings.LOG_LEVEL)
        settings.LOG_FORMAT = logging_config.get("format", settings.LOG_FORMAT)
        settings.LOG_FILE = logging_config.get("file", settings.LOG_FILE)
        settings.LOG_MAX_BYTES = logging_config.get("max_bytes", settings.LOG_MAX_BYTES)
        settings.LOG_BACKUP_COUNT = logging_config.get("backup_count", settings.LOG_BACKUP_COUNT)
    
    # Cache settings
    if "cache" in toml_config:
        cache_config = toml_config["cache"]
        settings.CACHE_DEFAULT_TTL = cache_config.get("default_ttl", settings.CACHE_DEFAULT_TTL)
        settings.CACHE_TASK_LIST_TTL = cache_config.get("task_list_ttl", settings.CACHE_TASK_LIST_TTL)
        settings.CACHE_USER_INFO_TTL = cache_config.get("user_info_ttl", settings.CACHE_USER_INFO_TTL)
    
    # API settings
    if "api" in toml_config:
        api_config = toml_config["api"]
        settings.API_TITLE = api_config.get("title", settings.API_TITLE)
        settings.API_DESCRIPTION = api_config.get("description", settings.API_DESCRIPTION)
        settings.API_VERSION = api_config.get("version", settings.API_VERSION)
        settings.API_DOCS_URL = api_config.get("docs_url", settings.API_DOCS_URL)
        settings.API_REDOC_URL = api_config.get("redoc_url", settings.API_REDOC_URL)
    
    return settings

# Load configuration
toml_config = load_config_from_toml()
config_settings = ConfigSettings()
config_settings = merge_toml_with_settings(toml_config, config_settings)

# Export the merged settings
settings = config_settings