from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, SessionLocal
from typing import List
from schemas.chatroom import EmotionChooseRequest, EmotionChooseResponse
from crud.chatroom import create_chatroom,get_chatroom,delete_chatroom
from crud.emotionchoose import create_emotion_chooses
from fastapi import HTTPException
router = APIRouter()

@router.post("/{user_id}", response_model=EmotionChooseResponse)
def create_chatroom_with_emotions(
    user_id: int,
    request: EmotionChooseRequest,
    db: Session = Depends(get_db)
):
    chatroom_id = create_chatroom(db, user_id)

    emotion_choose_ids = create_emotion_chooses(db, chatroom_id, request.emotion_ids)

    return {"chatroom_id": chatroom_id, "emotion_choose_ids": emotion_choose_ids}