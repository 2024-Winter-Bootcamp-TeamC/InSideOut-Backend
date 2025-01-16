from pydantic import BaseModel
from typing import List

# 클라이언트로부터 감정 ID 리스트를 받을 요청 모델
class EmotionChooseRequest(BaseModel):
    emotion_ids: List[int]

# 채팅방 ID와 감정 선택 ID 리스트를 반환할 응답 모델
class EmotionChooseResponse(BaseModel):
    chatroom_id: int
    emotion_choose_ids: List[int]