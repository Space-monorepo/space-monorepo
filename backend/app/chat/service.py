from app.users.service import UserService
from app.chat.repository import ChatRepository
from app.chat.exceptions import UnauthorizedMessageAccessError
from app.chat.schema import MessageCreate, MessageResponse, MessageUpdate


class ChatService:
    def __init__(self, db):
        self.db = db
        self.repository = ChatRepository(db)
        self.user_service = UserService(db)

    def send_message(self, sender_id: str, message: MessageCreate) -> MessageResponse:
        # Verifica se o receptor existe
        if not self.user_service.get_user_by_id(message.receiver_id):
            raise ValueError("Destinatário não encontrado")

        message_data = message.model_dump()
        message_data['sender_id'] = sender_id
        return self.repository.create_message(message_data)

    def get_message(self, message_id: str, requester_id: str) -> MessageResponse:
        message = self.repository.get_message_by_id(message_id)
        if message.sender_id != requester_id and message.receiver_id != requester_id:
            raise UnauthorizedMessageAccessError
        return message

    def update_message_status(self, message_id: str, status: str, requester_id: str) -> MessageResponse:
        message = self.get_message(message_id, requester_id)
        return self.repository.update_message(message_id, {'status': status})

    def delete_message(self, message_id: str, requester_id: str) -> bool:
        message = self.get_message(message_id, requester_id)
        return self.repository.delete_message(message_id)

    def get_user_conversation(self, user1_id: str, user2_id: str):
        return self.repository.get_conversation(user1_id, user2_id)