import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

from fastapi import WebSocket
from pydantic import BaseModel, Field, ValidationError
from pydantic.config import ConfigDict

from app.api.users.model import User

from .exceptions import EventHandlingError, EventValidationError

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='WebSocketEvent')
HandlerFunc = Callable[[WebSocket, User, T], None]
AsyncHandlerFunc = Callable[[WebSocket, User, T], Any]


class WebSocketEvent(BaseModel):
    """Base event for WebSocket."""

    type: str = Field(..., description='Event type')
    timestamp: Optional[float] = Field(None, description='Event timestamp')
    request_id: Optional[str] = Field(None, description='Request ID')

    model_config = ConfigDict(
        extra='allow',
        use_enum_values=True,
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode='json', exclude_none=True)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        try:
            return cls.model_validate(data)
        except ValidationError as e:
            raise EventValidationError(f'Invalid event data for {cls.__name__}: {e}')

    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise EventValidationError(f'Invalid JSON for event: {e}')


class EventResponse(BaseModel):
    """Standard response for WebSocket events."""

    success: bool = Field(..., description='Operation success')
    message: Optional[str] = Field(None, description='Response message')
    data: Optional[Dict[str, Any]] = Field(None, description='Response data')
    error_code: Optional[str] = Field(None, description='Error code')
    request_id: Optional[str] = Field(None, description='Request ID')

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode='json', exclude_none=True)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    model_config = ConfigDict(
        extra='allow',
        use_enum_values=True,
    )


class EventHandler(ABC):
    """Base handler for domain-specific events."""

    def __init__(self, namespace: str):
        self.namespace = namespace
        self._event_handlers: Dict[str, Union[HandlerFunc, AsyncHandlerFunc]] = {}
        self._event_types: Dict[str, Type[WebSocketEvent]] = {}
        self.register_events()

    @abstractmethod
    def register_events(self) -> None:
        """Register event types and handlers."""
        pass

    def register_event_type(
        self,
        event_type: str,
        event_class: Type[WebSocketEvent],
        handler: Union[HandlerFunc, AsyncHandlerFunc],
    ) -> None:
        self._event_types[event_type] = event_class
        self._event_handlers[event_type] = handler
        logger.debug(f"Event '{event_type}' registered in namespace '{self.namespace}'")

    def get_event_class(self, event_type: str) -> Optional[Type[WebSocketEvent]]:
        return self._event_types.get(event_type)

    def get_handler(
        self, event_type: str
    ) -> Optional[Union[HandlerFunc, AsyncHandlerFunc]]:
        return self._event_handlers.get(event_type)

    def get_supported_events(self) -> List[str]:
        return list(self._event_types.keys())

    async def handle_event(
        self, websocket: WebSocket, user: User, event_data: Dict[str, Any]
    ) -> Optional[EventResponse]:
        event_type = event_data.get('type')
        if not event_type:
            raise EventHandlingError('Event type is required')

        event_class = self.get_event_class(event_type)
        if not event_class:
            raise EventHandlingError(f'Unknown event type: {event_type}')

        handler = self.get_handler(event_type)
        if not handler:
            raise EventHandlingError(f'No handler for event type: {event_type}')

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

        try:
            if asyncio.iscoroutinefunction(handler):
                result = await handler(websocket, user, event)
            else:
                result = handler(websocket, user, event)

            if result is None:
                return EventResponse(
                    success=True,
                    message='Event processed successfully',
                    data=None,
                    error_code=None,
                    request_id=event.request_id,
                )
            elif isinstance(result, EventResponse):
                return result
            else:
                return EventResponse(
                    success=True,
                    message=None,
                    data=result if isinstance(result, dict) else {'result': result},
                    error_code=None,
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
    """Registry of event handlers by namespace."""

    def __init__(self):
        self._handlers: Dict[str, EventHandler] = {}

    def register_handler(self, namespace: str, handler: EventHandler) -> None:
        if namespace in self._handlers:
            logger.warning(f"Overriding handler for namespace '{namespace}'")

        self._handlers[namespace] = handler
        logger.info(f"Event handler registered for namespace '{namespace}'")

    def get_handler(self, namespace: str) -> Optional[EventHandler]:
        return self._handlers.get(namespace)

    def get_supported_namespaces(self) -> List[str]:
        return list(self._handlers.keys())

    def get_all_event_types(self) -> Dict[str, List[str]]:
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
        handler = self.get_handler(namespace)
        if not handler:
            raise EventHandlingError(f'No handler registered for namespace: {namespace}')

        return await handler.handle_event(websocket, user, event_data)


class PingEvent(WebSocketEvent):
    """Event for ping/pong heartbeat mechanism."""

    type: str = Field(default="ping", description="Event type")


class JoinRoomEvent(WebSocketEvent):
    """Event for joining a room."""

    type: str = Field(default="join_room", description="Event type")
    room_id: str = Field(..., description="Room identifier")


class LeaveRoomEvent(WebSocketEvent):
    """Event for leaving a room."""

    type: str = Field(default="leave_room", description="Event type")
    room_id: str = Field(..., description="Room identifier")


class ErrorEvent(WebSocketEvent):
    """Event for reporting errors."""

    type: str = Field(default="error", description="Event type")
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")


event_registry = EventRegistry()
