from fastapi import APIRouter, Depends, HTTPException, status
from pymongo import MongoClient
from app.core.database import get_db
from app.auth.deps import get_current_user
from app.users.schema import UserResponse
from app.chat.schema import MessageCreate, MessageResponse, MessageUpdate
from app.chat.service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/send", response_model=MessageResponse, status_code=201)
def send_message(
    message: MessageCreate,
    db: MongoClient = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    try:
        return ChatService(db).send_message(current_user.id, message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/messages/{message_id}", response_model=MessageResponse)
def get_message(
    message_id: str,
    db: MongoClient = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    try:
        return ChatService(db).get_message(message_id, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.patch("/messages/{message_id}", response_model=MessageResponse)
def mark_as_read(
    message_id: str,
    db: MongoClient = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    try:
        return ChatService(db).update_message_status(message_id, "read", current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/messages/{message_id}", response_model=bool)
def delete_message(
    message_id: str,
    db: MongoClient = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    try:
        return ChatService(db).delete_message(message_id, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/conversation/{user_id}", response_model=list[MessageResponse])
def get_conversation(
    user_id: str,
    db: MongoClient = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    try:
        return ChatService(db).get_user_conversation(current_user.id, user_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))