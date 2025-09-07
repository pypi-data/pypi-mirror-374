"""
Environment configuration management.

Handles switching between development and production environments.
"""

import os
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class Environment(str, Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class EnvironmentConfig(BaseModel):
    """Environment configuration settings with all system URLs and settings."""
    
    model_config = ConfigDict(
        # Add any specific config here if needed
    )
    
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Current environment"
    )
    
    debug: bool = Field(
        default=True,
        description="Enable debug mode"
    )
    
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    # System URLs - environment-aware
    redis_url: str = Field(
        default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        description="Redis connection URL"
    )
    
    max_workers: int = Field(
        default_factory=lambda: int(os.getenv("MAX_WORKERS", "10")),
        description="Maximum number of workers"
    )
    
    @classmethod
    def from_env(cls) -> "EnvironmentConfig":
        """Create config from environment variables."""
        env_name = os.getenv("UNREALON_ENV", "development").lower()
        
        # Map environment names
        env_mapping = {
            "dev": Environment.DEVELOPMENT,
            "development": Environment.DEVELOPMENT,
            "prod": Environment.PRODUCTION,
            "production": Environment.PRODUCTION,
            "test": Environment.TESTING,
            "testing": Environment.TESTING,
        }
        
        environment = env_mapping.get(env_name, Environment.DEVELOPMENT)
        
        return cls(
            environment=environment,
            debug=environment != Environment.PRODUCTION,
            log_level=os.getenv("UNREALON_LOG_LEVEL", "DEBUG" if environment != Environment.PRODUCTION else "INFO")
        )
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == Environment.TESTING
    
    @property
    def websocket_url(self) -> str:
        """Get WebSocket URL based on environment."""
        # Check explicit env var first
        if ws_url := os.getenv("WEBSOCKET_URL"):
            return ws_url
        
        if self.is_production:
            return "wss://ws.unrealon.com/ws"
        elif self.is_development:
            return "ws://localhost:8001/ws"  # RPC server port
        else:  # testing
            return "ws://localhost:8001/ws"
    
    @property
    def api_url(self) -> str:
        """Get API URL based on environment."""
        # Check explicit env var first
        if api_url := os.getenv("API_URL"):
            return api_url
        
        if self.is_production:
            return "https://api-m.unrealon.com"
        elif self.is_development:
            return "http://localhost:8002"  # Backend server port
        else:  # testing
            return "http://localhost:8002"
    
    @property
    def django_api_url(self) -> str:
        """Get Django API URL based on environment."""
        # Check explicit env var first
        if api_url := os.getenv("DJANGO_API_URL"):
            return api_url
        
        if self.is_production:
            return "https://api.unrealon.com"
        elif self.is_development:
            return "http://localhost:8000"  # Django server port
        else:  # testing
            return "http://localhost:8000"


# Global config instance
_environment_config: Optional[EnvironmentConfig] = None


def get_environment_config() -> EnvironmentConfig:
    """Get the global environment configuration."""
    global _environment_config
    
    if _environment_config is None:
        _environment_config = EnvironmentConfig.from_env()
    
    return _environment_config


def set_environment_config(config: EnvironmentConfig) -> None:
    """Set the global environment configuration."""
    global _environment_config
    _environment_config = config
