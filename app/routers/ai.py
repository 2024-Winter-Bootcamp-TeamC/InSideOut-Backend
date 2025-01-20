# app/routers/ai.py
from fastapi import APIRouter, HTTPException
from utils.prompt import PROMPTS, RULES
from pydantic import BaseModel
from typing import List
from fastapi.responses import StreamingResponse
import anthropic
import asyncio
import os

router = APIRouter()

# .env에서 API 키 가져옴
api_key = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=api_key)
class UserInput(BaseModel):
    prompt: str
    emotions: List[str]
  

@router.post("/ask-ai")
async def ask_ai(user_input: UserInput):
    """
    사용자의 질문을 Claude API로 전달하고, SSE 방식으로 응답을 실시간 스트림으로 보냅니다.
    """
    async def event_stream():
        try:
            # 프롬프트 생성
            system_prompt = "\n".join([f"{emotion}: {PROMPTS[emotion]}" for emotion in user_input.emotions])
            full_prompt = (
                f"{RULES}\n\n"
                f"사용자: {user_input}\n"
                
            )

            # Claude API 스트림 호출
            with client.messages.stream(
                max_tokens=600,
                system=(
                    f"{system_prompt}"
            ),
                messages=[
       
        {"role": "user", "content": f"{full_prompt}"},
    ],
                model="claude-3-5-haiku-20241022",
            ) as stream:
                # Claude의 스트림 데이터를 SSE로 변환하여 클라이언트로 전달
                for text in stream.text_stream:
                    data = {"type": "content_block_delta", "content": text}
                    yield f"data: {data}\n\n"  # SSE 포맷
                    await asyncio.sleep(0)  # 스트림 유지

        except Exception as e:
            # 에러가 발생하면 SSE로 에러 메시지를 전송
            yield f"event: error\ndata: {str(e)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/report-ai", tags=["AI"])
def report(request: createRequest):
    """
    AI를 통해 리포트에 들어가야 할 데이터를 생성하는 엔드포인트
    """
    try:
        response = create_report(
            client_message=request.client_message, 
            emotion_message=request.emotion_message
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))