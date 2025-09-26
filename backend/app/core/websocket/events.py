"""
Type-safe event system for WebSocket communication.

This module provides a robust, extensible event system that allows different
domains to register their own event handlers while maintaining type safety
and consistent error handling.

Key features:
- Type-safe event definitions using Pydantic
- Pluggable event handlers per domain/namespace
- Event validation and serialization
- Centralized event routing and dispatch
- Support for both synchronous and asynchronous handlers
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Literal, Optional, Type, TypeVar, Union
from uuid import UUID

from fastapi import WebSocket
from pydantic import BaseModel, Field, ValidationError

from app.api.users.model import User

from .exceptions import EventHandlingError, EventValidationError

logger = logging.getLogger(__name__)

# Type variables for generic event handling
T = TypeVar('T', bound='WebSocketEvent')
HandlerFunc = Callable[[WebSocket, User, T], None]
AsyncHandlerFunc = Callable[[WebSocket, User, T], Any]  # Awaitable


class WebSocketEvent(BaseModel):
    """
    Base class for all WebSocket events.

    All domain-specific events should inherit from this class to ensure
    consistent structure and validation.
    """

    type: str = Field(..., description='Event type identifier')
    timestamp: Optional[float] = Field(None, description='Event timestamp')
    request_id: Optional[str] = Field(None, description='Request ID for tracking')

    class Config:
        # Allow extra fields for domain-specific data
        extra = 'allow'
        # Use enum values for serialization
        use_enum_values = True
        # Generate schema with examples
        json_schema_extra = {
            'example': {
                'type': 'example_event',
                'timestamp': 1703001600.0,
                'request_id': 'req_123',
            }
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for JSON serialization."""
        return self.model_dump(mode='json', exclude_none=True)

    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create event instance from dictionary."""
        try:
            return cls.model_validate(data)
        except ValidationError as e:
            raise EventValidationError(f'Invalid event data for {cls.__name__}: {e}')

    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        """Create event instance from JSON string."""
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise EventValidationError(f'Invalid JSON for event: {e}')


class EventResponse(BaseModel):
    """
    Response structure for WebSocket events.

    Provides consistent response format across all domains.
    """

    success: bool = Field(..., description='Whether the operation was successful')
    message: Optional[str] = Field(None, description='Response message')
    data: Optional[Dict[str, Any]] = Field(None, description='Response data')
    error_code: Optional[str] = Field(None, description='Error code if failed')
    request_id: Optional[str] = Field(None, description='Original request ID')

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return self.model_dump(mode='json', exclude_none=True)

    def to_json(self) -> str:
        """Convert response to JSON string."""
        return json.dumps(self.to_dict())


class EventHandler(ABC):
    """
    Abstract base class for domain-specific event handlers.

    Each domain (chat, notifications, etc.) should implement this interface
    to handle their specific events.
    """

    def __init__(self, namespace: str):
        self.namespace = namespace
        self._event_handlers: Dict[str, Union[HandlerFunc, AsyncHandlerFunc]] = {}
        self._event_types: Dict[str, Type[WebSocketEvent]] = {}
        self.register_events()

    @abstractmethod
    def register_events(self) -> None:
        """
        Register event types and their handlers.

        This method should be implemented by each domain to register
        their specific event types and handlers.
        """
        pass

    def register_event_type(
        self,
        event_type: str,
        event_class: Type[WebSocketEvent],
        handler: Union[HandlerFunc, AsyncHandlerFunc],
    ) -> None:
        """Register an event type with its handler."""
        self._event_types[event_type] = event_class
        self._event_handlers[event_type] = handler
        logger.debug(
            f"Registered event type '{event_type}' in namespace '{self.namespace}'"
        )

    def get_event_class(self, event_type: str) -> Optional[Type[WebSocketEvent]]:
        """Get the event class for a given event type."""
        return self._event_types.get(event_type)

    def get_handler(
        self, event_type: str
    ) -> Optional[Union[HandlerFunc, AsyncHandlerFunc]]:
        """Get the handler function for a given event type."""
        return self._event_handlers.get(event_type)

    def get_supported_events(self) -> List[str]:
        """Get list of supported event types."""
        return list(self._event_types.keys())

    async def handle_event(
        self, websocket: WebSocket, user: User, event_data: Dict[str, Any]
    ) -> Optional[EventResponse]:
        """
        Handle an incoming event.

        Args:
            websocket: The WebSocket connection
            user: The authenticated user
            event_data: Raw event data dictionary

        Returns:
            Optional response to send back to client

        Raises:
            EventHandlingError: If event handling fails
        """
        event_type = event_data.get('type')
        if not event_type:
            raise EventHandlingError('Event type is required')

        # Get event class and handler
        event_class = self.get_event_class(event_type)
        if not event_class:
            raise EventHandlingError(f'Unknown event type: {event_type}')

        handler = self.get_handler(event_type)
        if not handler:
            raise EventHandlingError(f'No handler for event type: {event_type}')

        # Validate and create event instance
        try:
            event = event_class.from_dict(event_data)
        except EventValidationError as e:
            logger.error(f'Event validation failed for {event_type}: {e}')
            return EventResponse(
                success=False,
                message=str(e),
                error_code='VALIDATION_ERROR',
                request_id=event_data.get('request_id'),
            )

        # Execute handler
        try:
            # Check if handler is async
            if asyncio.iscoroutinefunction(handler):
                result = await handler(websocket, user, event)
            else:
                result = handler(websocket, user, event)

            # Return success response if no explicit response
            if result is None:
                return EventResponse(
                    success=True,
                    message='Event processed successfully',
                    request_id=event.request_id,
                )
            elif isinstance(result, EventResponse):
                return result
            else:
                # Assume result is data to include in response
                return EventResponse(
                    success=True,
                    data=result if isinstance(result, dict) else {'result': result},
                    request_id=event.request_id,
                )

        except Exception as e:
            logger.error(f'Handler error for {event_type}: {e}', exc_info=True)
            return EventResponse(
                success=False,
                message=f'Handler error: {str(e)}',
                error_code='HANDLER_ERROR',
                request_id=event.request_id,
            )


class EventRegistry:
    """
    Registry for managing event handlers across different namespaces.

    This provides a centralized way to register and retrieve event handlers
    for different domains while maintaining separation of concerns.
    """

    def __init__(self):
        self._handlers: Dict[str, EventHandler] = {}

    def register_handler(self, namespace: str, handler: EventHandler) -> None:
        """Register an event handler for a specific namespace."""
        if namespace in self._handlers:
            logger.warning(f"Overriding existing handler for namespace '{namespace}'")

        self._handlers[namespace] = handler
        logger.info(f"Registered event handler for namespace '{namespace}'")

    def get_handler(self, namespace: str) -> Optional[EventHandler]:
        """Get the event handler for a specific namespace."""
        return self._handlers.get(namespace)

    def get_supported_namespaces(self) -> List[str]:
        """Get list of supported namespaces."""
        return list(self._handlers.keys())

    def get_all_event_types(self) -> Dict[str, List[str]]:
        """Get all event types grouped by namespace."""
        return {
            namespace: handler.get_supported_events()
            for namespace, handler in self._handlers.items()
        }

    async def handle_event(
        self,
        namespace: str,
        websocket: WebSocket,
        user: User,
        event_data: Dict[str, Any],
    ) -> Optional[EventResponse]:
        """
        Route and handle an event for a specific namespace.

        Args:
            namespace: The target namespace
            websocket: WebSocket connection
            user: Authenticated user
            event_data: Raw event data

        Returns:
            Event response or None

        Raises:
            EventHandlingError: If namespace not found or handling fails
        """
        handler = self.get_handler(namespace)
        if not handler:
            raise EventHandlingError(f'No handler registered for namespace: {namespace}')

        return await handler.handle_event(websocket, user, event_data)


# Global event registry instance
event_registry = EventRegistry()


# Common event types that can be used across domains
class PingEvent(WebSocketEvent):
    """Ping event for connection health checks."""

    type: Literal['ping'] = Field(default='ping')


class PongEvent(WebSocketEvent):
    """Pong response event."""

    type: Literal['pong'] = Field(default='pong')


class ErrorEvent(WebSocketEvent):
    """Error event for communicating errors to clients."""

    type: Literal['error'] = Field(default='error')
    error_message: str = Field(..., description='Error message')
    error_code: Optional[str] = Field(None, description='Error code')


class JoinRoomEvent(WebSocketEvent):
    """Generic event for joining a room."""

    type: Literal['join_room'] = Field(default='join_room')
    room_id: str = Field(..., description='Room identifier')
    room_type: Optional[str] = Field(None, description='Type of room')


class LeaveRoomEvent(WebSocketEvent):
    """Generic event for leaving a room."""

    type: Literal['leave_room'] = Field(default='leave_room')
    room_id: str = Field(..., description='Room identifier')


class UserStatusEvent(WebSocketEvent):
    """Event for user status changes (online/offline)."""

    type: Literal['user_status'] = Field(default='user_status')
    user_id: UUID = Field(..., description='User ID')
    status: str = Field(..., description='User status')
    room_id: Optional[str] = Field(None, description='Room context')
