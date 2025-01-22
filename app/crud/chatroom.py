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

def get_chatroom(db: Session, chatroom_id: int) :
    chatroom = db.query(Chatroom).filter(Chatroom.id == chatroom_id).first()
    if not chatroom:
        raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없습니다.")
    return chatroom

def delete_chatroom(db: Session, chatroom_id: int) :
    chatroom = db.query(Chatroom).filter(Chatroom.id == chatroom_id).first()
    if not chatroom:
        raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없습니다.")
    db.delete(chatroom)
    db.commit()
    db.refresh(chatroom)
    return chatroom.id