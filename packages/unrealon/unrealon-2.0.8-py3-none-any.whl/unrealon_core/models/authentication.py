"""
Authentication models for UnrealOn system.

Provides Pydantic models for API key authentication between services.
"""
from typing import Optional, List
from pydantic import Field

from .base import UnrealOnBaseModel


class APIKeyAuthRequest(UnrealOnBaseModel):
    """API key authentication request."""
    api_key: str = Field(min_length=1, description="API key for authentication")
    parser_id: str = Field(min_length=1, description="Parser requesting authentication")


class APIKeyAuthResponse(UnrealOnBaseModel):
    """API key authentication response."""
    success: bool = Field(description="Whether authentication was successful")
    user_id: Optional[int] = Field(default=None, description="Authenticated user ID")
    username: Optional[str] = Field(default=None, description="Authenticated username")
    permissions: List[str] = Field(default_factory=list, description="User permissions")
    error: Optional[str] = Field(default=None, description="Error message if failed")
