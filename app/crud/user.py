from models import User
from schemas.user import UserPostRequest
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

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

def login_user(nickname: str, password: str, db: Session):
    user = db.query(User).filter(User.nickname == nickname).first()
    if user is None:
        raise HTTPException(status_code=404, detail="The nickname doesn't exist")

    if user.password != password:
        raise HTTPException(status_code=400, detail="The password is not correct")

    return {"status": "success", "message": "Successfully logged in", "user_id": user.id}

def delete_user(user_id :int, db :Session):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_deleted:
        raise HTTPException(status_code=400, detail="User already deleted")
    
    user.is_deleted = True
    user.updated_at = datetime.now()

    db.commit()

    return{"status": "success", "message": "User deleted successfully"}
    


        