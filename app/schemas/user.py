from pydantic import BaseModel


class UserPostRequest(BaseModel):
    nickname: str
    password: str

class UserInDB(UserPostRequest):
    id: int
    created_at: str
    updated_at: str
    is_deleted: bool

class UserPostResponse(BaseModel):
    id: int