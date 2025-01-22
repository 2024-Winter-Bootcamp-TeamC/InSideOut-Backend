from fastapi import APIRouter,Depends
from database import get_db
from sqlalchemy.orm import Session
from crud.emotions import get_emotions


router = APIRouter()

@router.get("/{user_id}", description="7가지 감정 요청")
def seven_emotion(user_id: int, db: Session = Depends(get_db)):
    result = get_emotions(user_id, db)
    return result
