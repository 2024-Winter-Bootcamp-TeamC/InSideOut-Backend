from pydantic import BaseModel


class UserPostRequest(BaseModel):
    nickname: str
    password: str

class UserLoginRequest(UserPostRequest):
    pass

class UserLoginResponse(BaseModel):
    id: int

# 사용자 입력 모델
class UserInput(BaseModel):
    message: str



    