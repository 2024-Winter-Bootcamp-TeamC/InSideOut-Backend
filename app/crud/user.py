from models import User
from schemas.user import UserPostRequest, UserPostResponse
from sqlalchemy.orm import Session

def create_user (new_user: UserPostRequest, db: Session):
    user = User(
            nickname = new_user.nickname,
            password = new_user.password
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user
        