from pydantic import BaseModel
from typing import List

class EmotionChooseRequest(BaseModel):
    emotion_ids: List[int]

class EmotionChooseResponse(BaseModel):
    chatroom_id: int
    emotion_choose_ids: List[int]