"""
Clean driver configuration without hardcoded values.
"""

import os
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, computed_field

try:
    from unrealon_core.config.environment import get_environment_config
    UNREALON_CORE_AVAILABLE = True
except ImportError:
    UNREALON_CORE_AVAILABLE = False


class DriverMode(str, Enum):
    """Driver operation modes."""
    STANDALONE = "standalone"
    DAEMON = "daemon"


class DriverConfig(BaseModel):
    """
    Clean driver configuration.
    No hardcoded presets - user configures everything explicitly.
    """
    
    # Basic settings
    name: str = Field(..., description="Driver name")
    mode: DriverMode = Field(default=DriverMode.STANDALONE, description="Operation mode")
    
    # WebSocket connection (auto-detected)
    websocket_url: Optional[str] = Field(default=None, description="Manual WebSocket URL override")
    websocket_timeout: int = Field(default=30, description="WebSocket timeout seconds")
    
    @computed_field
    @property
    def effective_websocket_url(self) -> Optional[str]:
        """
        Auto-detect WebSocket URL from multiple sources.
        
        Priority:
        1. Explicit websocket_url field
        2. Environment variables (UNREALON_WEBSOCKET_URL, UNREALON_WS_URL, WS_URL)
        3. UnrealOn core environment config (if available)
        4. No default - return None if nothing configured
        """
        # 1. Explicit override
        if self.websocket_url:
            return self.websocket_url
        
        # 2. Environment variables
        env_url = (
            os.getenv('UNREALON_WEBSOCKET_URL') or 
            os.getenv('UNREALON_WS_URL') or
            os.getenv('WS_URL')
        )
        if env_url:
            return env_url
        
        # 3. Try unrealon_core environment config
        if UNREALON_CORE_AVAILABLE:
            try:
                env_config = get_environment_config()
                return env_config.websocket_url
            except Exception:
                pass  # Fallback gracefully if core config fails
        
        # 4. No default - return None if nothing is configured
        return None
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    
    # HTTP settings
    http_timeout: int = Field(default=30, description="HTTP timeout seconds")
    max_retries: int = Field(default=3, description="Max HTTP retries")
    
    # Browser settings
    browser_headless: bool = Field(default=True, description="Run browser headless")
    browser_timeout: int = Field(default=30, description="Browser timeout seconds")
    
    # Proxy settings
    proxy_enabled: bool = Field(default=False, description="Enable proxy rotation")
    proxy_rotation_interval: int = Field(default=300, description="Proxy rotation seconds")
    
    # Cache settings
    cache_enabled: bool = Field(default=True, description="Enable response caching")
    cache_ttl: int = Field(default=3600, description="Cache TTL seconds")
    
    # Threading
    max_workers: int = Field(default=4, description="Max thread workers")
    
    # Performance
    batch_size: int = Field(default=10, description="Batch processing size")
    
    model_config = {"extra": "forbid"}
    
    @classmethod
    def for_development(cls, name: str, **kwargs) -> "DriverConfig":
        """
        Create development configuration with sensible defaults.
        
        Args:
            name: Driver name
            **kwargs: Additional configuration overrides
        """
        defaults = {
            "name": name,
            "mode": DriverMode.STANDALONE,
            "log_level": "DEBUG",
            "browser_headless": False,
            "proxy_enabled": False,
            "cache_enabled": True,
            "max_workers": 2,
        }
        defaults.update(kwargs)
        return cls(**defaults)
    
    @classmethod
    def for_production(cls, name: str, **kwargs) -> "DriverConfig":
        """
        Create production configuration with performance and reliability defaults.
        
        Args:
            name: Driver name
            **kwargs: Additional configuration overrides
        """
        defaults = {
            "name": name,
            "mode": DriverMode.DAEMON,
            "log_level": "INFO",
            "browser_headless": True,
            "proxy_enabled": True,
            "cache_enabled": True,
            "max_workers": 4,
            "max_retries": 5,
            "http_timeout": 60,
            "browser_timeout": 60,
        }
        defaults.update(kwargs)
        return cls(**defaults)
    
    @classmethod
    def auto_detect(cls, name: str, **kwargs) -> "DriverConfig":
        """
        Auto-detect environment and create appropriate configuration.
        
        Uses UNREALON_ENV environment variable or unrealon_core config to determine environment.
        
        Args:
            name: Driver name
            **kwargs: Additional configuration overrides
        """
        # Try to detect environment
        env_name = os.getenv("UNREALON_ENV", "development").lower()
        
        # Try unrealon_core if available
        if UNREALON_CORE_AVAILABLE:
            try:
                env_config = get_environment_config()
                if env_config.is_production:
                    return cls.for_production(name, **kwargs)
                elif env_config.is_development:
                    return cls.for_development(name, **kwargs)
            except Exception:
                pass  # Fallback to env variable
        
        # Fallback to environment variable
        if env_name in ("prod", "production"):
            return cls.for_production(name, **kwargs)
        else:
            return cls.for_development(name, **kwargs)
