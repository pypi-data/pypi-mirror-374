"""
ARQ job name enums for UnrealOn system.

Centralized job name definitions used across all services.
"""
from enum import Enum


class ARQJobName(str, Enum):
    """
    ARQ job names used in the system.
    
    These are the job function names that can be enqueued
    and processed by ARQ workers.
    """
    
    # Driver management jobs
    REGISTER_DRIVER = "register_driver"
    DRIVER_DISCONNECT = "driver_disconnect"
    GET_DRIVER_STATUS = "get_driver_status"
    LIST_AVAILABLE_DRIVERS = "list_available_drivers"
    
    # Task management jobs
    ASSIGN_TASK_TO_DRIVER = "assign_task_to_driver"
    
    # System jobs
    PING = "ping"
    PROCESS_DRIVER_HEARTBEAT = "process_driver_heartbeat"
    
    # Lifecycle jobs
    STARTUP = "startup"
    SHUTDOWN = "shutdown"
