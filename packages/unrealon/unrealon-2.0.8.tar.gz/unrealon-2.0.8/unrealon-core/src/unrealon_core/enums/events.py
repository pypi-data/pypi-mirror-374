"""
Event type enums for UnrealOn system.

Centralized event type definitions used across all services.
"""
from enum import Enum


class EventType(str, Enum):
    """
    Event types used in Redis PubSub and system events.
    
    These events are used for communication between services:
    - RPC server publishes events
    - Django consumes events via Redis PubSub
    - System events are stored in database
    """
    
    # Driver lifecycle events
    DRIVER_REGISTER = "driver_register"
    DRIVER_DISCONNECT = "driver_disconnect"
    
    # Parser events (Django-specific naming)
    PARSER_REGISTERED = "parser_registered"
    PARSER_HEARTBEAT = "parser_heartbeat"
    PARSER_DISCONNECTED = "parser_disconnected"
    PARSER_ERROR = "parser_error"
    PARSER_LOG = "parser_log"
    
    # Session events
    SESSION_STARTED = "session_started"
    SESSION_COMPLETED = "session_completed"
    SESSION_FAILED = "session_failed"
    
    # Command events
    COMMAND_ISSUED = "command_issued"
    COMMAND_COMPLETED = "command_completed"
    COMMAND_FAILED = "command_failed"
    
    # System events
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    SYSTEM_ERROR = "system_error"


class SystemEventType(str, Enum):
    """
    System event types for Django database storage.
    
    These match the choices in Django's SystemEvent model.
    """
    
    # Parser events
    PARSER_REGISTERED = "parser_registered"
    PARSER_HEARTBEAT = "parser_heartbeat"
    PARSER_DISCONNECTED = "parser_disconnected"
    PARSER_ERROR = "parser_error"
    
    # Session events
    SESSION_STARTED = "session_started"
    SESSION_COMPLETED = "session_completed"
    SESSION_FAILED = "session_failed"
    
    # Command events
    COMMAND_ISSUED = "command_issued"
    COMMAND_COMPLETED = "command_completed"
    COMMAND_FAILED = "command_failed"
    
    # System events
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    SYSTEM_ERROR = "system_error"


class RedisEventType(str, Enum):
    """
    Redis PubSub event types.
    
    These are the event types published to Redis channels
    for inter-service communication.
    """
    
    # Driver lifecycle (from RPC to Django)
    DRIVER_REGISTER = "driver_register"
    DRIVER_DISCONNECT = "driver_disconnect"
    
    # Parser events (internal Django events)
    PARSER_HEARTBEAT = "parser_heartbeat"
    PARSER_LOG = "parser_log"
    
    # Session events
    SESSION_STARTED = "session_started"
    SESSION_COMPLETED = "session_completed"
    SESSION_FAILED = "session_failed"
    
    # Command events
    COMMAND_COMPLETED = "command_completed"
    COMMAND_FAILED = "command_failed"
