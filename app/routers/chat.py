from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
from schemas.user import UserInput
router = APIRouter()



@router.post("/test", tags=["Chats"])
async def stream(user_input: UserInput):
    """
    POST 요청으로 사용자 입력을 받고, SSE로 데이터를 스트림 방식으로 전송
    """
    async def event_stream():
        for i in range(10):  # 10개의 스트리밍 메시지
            yield f"data: Reply {i}: {user_input.message}\n\n"
            await asyncio.sleep(1)  # 1초 대기 (스트림 유지)

    return StreamingResponse(event_stream(), media_type="text/event-stream")