from bson import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection
from app.chat.exceptions import MessageNotFoundError
from app.chat.schema import MessageResponse, MessageUpdate

class ChatRepository:
    def __init__(self, db: MongoClient):
        self.db = db
        self.collection: Collection = db['messages']

    def create_message(self, message: dict) -> MessageResponse:
        result = self.collection.insert_one(message)
        new_message = self.collection.find_one({'_id': result.inserted_id})
        new_message['_id'] = str(new_message['_id'])
        return MessageResponse.model_validate(new_message)

    def get_message_by_id(self, message_id: str) -> MessageResponse:
        message = self.collection.find_one({'_id': ObjectId(message_id)})
        if not message:
            raise MessageNotFoundError
        message['_id'] = str(message['_id'])
        return MessageResponse.model_validate(message)

    def update_message(self, message_id: str, update_data: dict) -> MessageResponse:
        self.collection.update_one(
            {'_id': ObjectId(message_id)},
            {'$set': update_data}
        )
        return self.get_message_by_id(message_id)

    def delete_message(self, message_id: str) -> bool:
        result = self.collection.delete_one({'_id': ObjectId(message_id)})
        return result.deleted_count > 0

    def get_conversation(self, user1_id: str, user2_id: str):
        query = {
            '$or': [
                {'sender_id': user1_id, 'receiver_id': user2_id},
                {'sender_id': user2_id, 'receiver_id': user1_id}
            ]
        }
        messages = list(self.collection.find(query).sort('created_at', 1))

        for msg in messages:
            msg['_id'] = str(msg['_id'])
        return [MessageResponse.model_validate(msg) for msg in messages]