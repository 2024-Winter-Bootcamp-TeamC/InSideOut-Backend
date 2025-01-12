from fastapi import APIRouter ,Depends
from schemas.user import UserPostRequest,UserPostResponse
from crud import user as UserServices
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter()

@router.post("/signup",description="유저 회원가입")
def post_user(new_user:UserPostRequest, db : Session = Depends(get_db)):
    response = UserServices.create_user(new_user,db)
    return response

