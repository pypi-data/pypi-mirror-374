"""
Broadcast WebSocket Models.

Strictly typed models for broadcasting driver events to monitoring clients.
These are Server → Client messages for real-time monitoring.

Phase 2: Core Systems - WebSocket Bridge
"""

from typing import List, Optional
from pydantic import Field, ConfigDict

from ..base import UnrealOnBaseModel
from .base import WebSocketMessage, MessageType


class DriverBroadcastData(UnrealOnBaseModel):
    """Driver broadcast data payload - strictly typed."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    driver_id: str = Field(
        description="Unique driver identifier",
        min_length=1
    )
    
    driver_type: str = Field(
        description="Type of driver (e.g., 'universal', 'ecommerce')",
        min_length=1
    )
    
    status: str = Field(
        default="active",
        pattern=r"^(active|idle|busy|offline|error)$",
        description="Current driver status"
    )
    
    capabilities: List[str] = Field(
        default_factory=list,
        description="List of supported task types"
    )
    
    active_tasks: int = Field(
        default=0,
        ge=0,
        description="Number of currently active tasks"
    )
    
    completed_tasks: int = Field(
        default=0,
        ge=0,
        description="Total completed tasks since startup"
    )
    
    failed_tasks: int = Field(
        default=0,
        ge=0,
        description="Total failed tasks since startup"
    )
    
    uptime_seconds: float = Field(
        default=0.0,
        ge=0.0,
        description="Driver uptime in seconds"
    )
    
    last_seen: Optional[str] = Field(
        default=None,
        description="ISO timestamp of last heartbeat"
    )
    
    connected_at: Optional[str] = Field(
        default=None,
        description="ISO timestamp when driver connected"
    )
    
    disconnected_at: Optional[str] = Field(
        default=None,
        description="ISO timestamp when driver disconnected"
    )
    
    # Additional fields for complete driver information
    version: Optional[str] = Field(
        default=None,
        description="Driver version"
    )
    
    driver_name: Optional[str] = Field(
        default=None,
        description="Human-readable driver name"
    )
    
    environment: Optional[str] = Field(
        default=None,
        description="Driver environment (development, production, etc.)"
    )
    
    region: Optional[str] = Field(
        default=None,
        description="Driver region"
    )
    
    max_concurrent_tasks: Optional[int] = Field(
        default=None,
        ge=1,
        description="Maximum concurrent tasks"
    )
    
    tags: List[str] = Field(
        default_factory=list,
        description="Driver tags"
    )


class DriverRegisterBroadcast(WebSocketMessage):
    """Driver registration broadcast message (Server → Monitoring Clients)."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    type: MessageType = Field(
        default=MessageType.DRIVER_REGISTER
    )
    
    data: DriverBroadcastData = Field(
        description="Driver registration broadcast data"
    )


class DriverHeartbeatBroadcast(WebSocketMessage):
    """Driver heartbeat broadcast message (Server → Monitoring Clients)."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    type: MessageType = Field(
        default=MessageType.DRIVER_HEARTBEAT,
        frozen=True
    )
    
    data: DriverBroadcastData = Field(
        description="Driver heartbeat broadcast data"
    )


class DriverDisconnectBroadcast(WebSocketMessage):
    """Driver disconnect broadcast message (Server → Monitoring Clients)."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    type: MessageType = Field(
        default=MessageType.DRIVER_DISCONNECT,
        frozen=True
    )
    
    data: DriverBroadcastData = Field(
        description="Driver disconnect broadcast data"
    )
