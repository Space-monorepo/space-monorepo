"""
Chat WebSocket routes using the centralized WebSocket architecture.

This module provides the integration point between the centralized WebSocket
system and the chat domain. It registers the chat event handler and provides
a clean WebSocket endpoint for chat functionality.

The actual WebSocket handling is done by the centralized WebSocketManager,
while chat-specific logic is handled by the ChatEventHandler.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, WebSocket
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.websocket.manager import websocket_manager

from .websocket.handlers import ChatEventHandler
from .websocket.rooms import get_chat_room_manager

logger = logging.getLogger(__name__)


# Initialize chat WebSocket handling
def register_chat_websocket():
    """Register chat WebSocket handler with the global WebSocket manager."""
    chat_handler = ChatEventHandler('chat')
    websocket_manager.register_namespace_handler('chat', chat_handler)
    return chat_handler


chat_handler = register_chat_websocket()

# Router for WebSocket endpoint
router = APIRouter(prefix='/chat', tags=['chat-websocket'])


@router.websocket('/ws')
async def chat_websocket_endpoint(
    websocket: WebSocket,
    session: Session = Depends(get_db),
    conversation_id: Optional[str] = None,
):
    """
    WebSocket endpoint for chat functionality.

    This endpoint uses the centralized WebSocket manager to handle chat
    connections. All chat-specific logic is handled by the ChatEventHandler
    which is registered with the 'chat' namespace.

    Connection URL: ws://localhost:8000/chat/ws?token=your_jwt_token

    Optional query parameters:
    - token: JWT authentication token
    - conversation_id: Auto-join a specific conversation (optional)

    Supported Events:
    - send_message: Send a text message
    - send_message_with_attachment: Send message with file attachment
    - join_conversation: Join a conversation room
    - leave_conversation: Leave a conversation room
    - typing: Send typing indicator
    - stop_typing: Stop typing indicator
    - mark_message_read: Mark a message as read
    - bulk_mark_read: Mark multiple messages as read

    Response Events:
    - welcome: Connection established
    - message_sent: Message sent confirmation
    - message_received: New message received
    - user_typing: User started typing
    - user_stopped_typing: User stopped typing
    - message_read: Message read confirmation
    - conversation_joined: Joined conversation successfully
    - conversation_left: Left conversation successfully
    - user_joined_conversation: Another user joined
    - user_left_conversation: Another user left
    - chat_error: Error occurred
    """
    try:
        # Use the centralized WebSocket manager to handle the connection
        await websocket_manager.handle_connection(
            websocket=websocket, session=session, namespace='chat'
        )

    except Exception as e:
        logger.error(f'Chat WebSocket error: {e}', exc_info=True)
        try:
            await websocket.close(code=1011, reason='Internal server error')
        except Exception:
            pass


# Health check endpoint for WebSocket
@router.get('/ws/health')
async def websocket_health():
    """
    Health check endpoint for chat WebSocket service.

    Returns connection statistics and service status.
    """
    try:
        stats = websocket_manager.get_connection_stats()

        # Get chat-specific stats
        chat_stats = stats.get('namespaces', {}).get('chat', 0)

        return {
            'status': 'healthy',
            'service': 'chat_websocket',
            'chat_connections': chat_stats,
            'total_connections': stats.get('current_connections', 0),
            'supported_events': chat_handler.get_supported_events(),
        }

    except Exception as e:
        logger.error(f'WebSocket health check error: {e}')
        return {'status': 'unhealthy', 'service': 'chat_websocket', 'error': str(e)}


# Detailed statistics endpoint
@router.get('/ws/stats')
async def websocket_stats():
    """
    Detailed WebSocket statistics for monitoring and debugging.

    Returns comprehensive connection and room statistics.
    """
    try:
        # Get overall WebSocket stats
        general_stats = websocket_manager.get_connection_stats()

        # Get chat room manager for chat-specific stats
        chat_room_manager = get_chat_room_manager()
        chat_stats = chat_room_manager.get_chat_room_stats()

        return {
            'general': general_stats,
            'chat': chat_stats,
            'timestamp': websocket_manager._stats.get('last_updated', 'N/A'),
        }

    except Exception as e:
        logger.error(f'WebSocket stats error: {e}')
        return {'error': str(e)}


# Export for easy importing
__all__ = ['router', 'chat_handler', 'chat_websocket_endpoint']
