from sqlalchemy.orm import Session
from models import Chatroom, User
from fastapi import HTTPException

def create_chatroom(db: Session, user_id: int) -> int:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    chatroom = Chatroom(user_id=user_id)
    db.add(chatroom)
    db.commit()
    db.refresh(chatroom)
    return chatroom.id