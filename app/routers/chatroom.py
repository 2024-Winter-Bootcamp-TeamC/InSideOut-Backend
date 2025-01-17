# routers/chatroom.py : SSE 및 스트림 방식 라우터 구현

from fastapi import APIRouter, Depends, Query
# from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db, SessionLocal
# from crud.chatroom import save_chat_message
# from crud.ai import get_ai_responses_stream
from typing import List
import redis
import json

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# # Redis 클라이언트 초기화
# redis_client = redis.Redis(host='localhost', port=6379, db=0) # 설정 다시 확인하기

# # SSE 기반 실시간 채팅
# @router.get("/stream", description="SSE 방식 실시간 상담 진행")
# async def stream_chatroom(
#     chatroom_id: int,
#     prompt: str,
#     emotions: List[str] = Query(...),
#     db: Session = Depends(get_db)
# ):
#     """
#     AI와 실시간 상담 진행.
#     :param chatroom_id: 생성된 채팅방 ID
#     :param prompt: 사용자가 입력한 초기 메시지
#     :param emotions: 선택한 감정 AI 리스트
#     :param db: 데이터베이스 세션
#     """
#     async def event_stream():
#         # Redis에서 연결할 채팅방 id 설정
#         redis_key = f"chatroom:{chatroom_id}:messages"

#         # AI 응답. 각 감정 AI에 대해 "순차적"으로 스트림 방식으로 받음.
#         async for emotion, response in get_ai_responses_stream(prompt, emotions):
#             # 저장하는 감정ai의 응답
#             message = {
#                 "speaker": "AI",
#                 "emotion": emotion,
#                 "message": response
#             }

#             # Redis 리스트에 메시지 추가
#             redis_client.rpush(redis_key, json.dumps(message))

#             # SSE로 클라이언트에 실시간 스트리밍 전송
#             yield f"data: {{\"emotion\": \"{emotion}\", \"response\": \"{response}\"}}\n\n"

#     return StreamingResponse(event_stream(), media_type="text/event-stream")




# # "대화끝내기" 버튼 클릭시, SSE 연결 종료
# @router.post("/end", description="SSE 연결 종료 및 데이터 저장 완료")
# def end_chatroom(chatroom_id: int, db: Session = Depends(get_db)):
#     """
#     SSE 연결 종료시. 그동안 Redis에 저장되어있던 대화 내역을 가져와 MySQL에 저장.
#     :param chatroom_id: 채팅방 ID
#     :param db: 데이터베이스 세션
#     """
#     # Redis에서 대화내역 가져옴.
#     redis_key = f"chatroom:{chatroom_id}:messages"
#     chat_history = redis_client.lrange(redis_key, 0, -1)  # Redis 리스트에서 모든 데이터 가져오기

#     if chat_history:
#         messages = [json.loads(msg) for msg in chat_history]  # JSON 문자열 -> Python 객체로 변환
#         for msg in messages:
#             save_chat_message(  # 대화내용 MySQL에 저장
#                 db=db,
#                 chatroom_id=chatroom_id,
#                 sender=msg["speaker"],  # 메시지 발신자(사용자 or 감정AI)
#                 emotion=msg.get("emotion"),  # 감정AI 이름 (AI의 메시지인 경우)
#                 message=msg["message"]  # 메시지 내용
#             )

#         # Redis에서 대화내역 삭제
#         redis_client.delete(redis_key)

#     return {"message": "Chatroom ended successfully and messages saved", "chatroom_id": chatroom_id}





#-------------------------------------
# @router.post("/{user_id}", response_model=EmotionChooseResponse)
# def create_chatroom_with_emotions(
#     user_id: int,
#     request: EmotionChooseRequest,
#     db: Session = Depends(get_db)
# ):
#     chatroom_id = create_chatroom(db, user_id)

#     emotion_choose_ids = create_emotion_chooses(db, chatroom_id, request.emotion_ids)

#     return {"chatroom_id": chatroom_id, "emotion_choose_ids": emotion_choose_ids}
#-------------------------------------
