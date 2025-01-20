# app/routers/ai.py
from fastapi import APIRouter, HTTPException
from utils.prompt import PROMPTS, RULES
from fastapi.responses import StreamingResponse
import anthropic
import asyncio
import os
from crud.ai import  create_report
from schemas.ai import UserInput


router = APIRouter()

api_key = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=api_key)

@router.post("/ask-ai")
async def ask_ai(user_input: UserInput):
    """
    사용자의 질문을 Claude API로 전달하고, SSE 방식으로 응답을 실시간 스트림으로 보냅니다.
    """
    async def event_stream():
        try:

            system_prompt = "\n".join([f"{emotion}: {PROMPTS[emotion]}" for emotion in user_input.emotions])
            full_prompt = (
                f"{RULES}\n\n"
                f"사용자: {user_input}\n"
                
            )

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
                for text in stream.text_stream:
                    data = {"type": "content_block_delta", "content": text}
                    yield f"data: {data}\n\n"  
                    await asyncio.sleep(0)  

        except Exception as e:
            yield f"event: error\ndata: {str(e)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@router.post("/report-ai", tags=["AI"])
def report(client_message:str, emotion_message:str):

    response = create_report(
        client_message=client_message, 
        emotion_message=emotion_message
    )
    return response