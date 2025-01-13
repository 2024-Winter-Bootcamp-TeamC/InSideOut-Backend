from models import User
from schemas.user import UserPostRequest
from sqlalchemy.orm import Session
from fastapi import HTTPException

def create_user (new_user: UserPostRequest, db: Session):
    user = User(
            nickname = new_user.nickname,
            password = new_user.password
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def find_user(user_id :int ,db :Session)  :
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return HTTPException(status_code=404, detail="User not found")
    return user.nickname
        