# app/routers/chat.py
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import asyncio
from schemas.chat import UserInput, Discussion
from database import get_db
from sqlalchemy.orm import Session
from crud.ai import ValidateUserandChatRoom
from crud.chat import generate_event_stream

router = APIRouter()

@router.get("/sse/{chatroom_id}", description="SSE 첫 연결" ,tags=["Chat"])
async def sse_connect(chatroom_id: int):
    """
    SSE 핑 테스트용 API
    """
    async def ping_stream():
        while True:
            yield "data: ping\n\n"  
            await asyncio.sleep(30) 

    return StreamingResponse(ping_stream(), media_type="text/event-stream")

@router.post("/{chatroom_id}/messages", description="기본대화 모드?", tags=["Chat"])
async def ask_ai_messages(chatroom_id: int, user_id: int, user_input: UserInput, db: Session = Depends(get_db)):
    ValidateUserandChatRoom(user_id, chatroom_id, db)
    return StreamingResponse(
        generate_event_stream(user_id, chatroom_id, user_input.emotions, db,mode="messages", user_prompt=user_input.user_prompt),
        media_type="text/event-stream",
    )

@router.post("/{chatroom_id}/discussions", description="논쟁 모드?", tags=["Chat"])
async def ask_ai_discussions(chatroom_id: int, user_id: int, discuss: Discussion, db: Session = Depends(get_db)):
    ValidateUserandChatRoom(user_id, chatroom_id, db)
    return StreamingResponse(
        generate_event_stream(user_id, chatroom_id, discuss.emotions, db, mode="discussions"),
        media_type="text/event-stream",
    )
