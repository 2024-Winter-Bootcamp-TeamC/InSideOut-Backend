# app/routers/chat.py
from fastapi import APIRouter, HTTPException
from utils.prompt import PROMPTS, RULES
from pydantic import BaseModel
from typing import List
from fastapi.responses import StreamingResponse
import anthropic
import asyncio
import os
from io import BytesIO
import base64 
from elevenlabs.client import ElevenLabs
import json
import logging
from utils.tts import text_to_speech_stream, emotion_to_voice_id
from schemas.chatroom import createRequest, create_report

router = APIRouter()

# .env에서 API 키 가져옴
api_key = os.getenv("ANTHROPIC_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")


client = anthropic.Anthropic(api_key=api_key)
tts_client = ElevenLabs(api_key=elevenlabs_api_key)

logging.basicConfig(level=logging.INFO)

class UserInput(BaseModel):
    prompt: str
    emotions: List[str]

# SSE 첫 연결(GET) + 핑 테스트 API
@router.get("/sse/{chatroom_id}", description="SSE 첫 연결" ,tags=["Chat"])
async def sse_connect(chatroom_id: int):
    """
    SSE 핑 테스트용 API
    """
    async def ping_stream():
        while True:
            yield "data: ping\n\n"  
            await asyncio.sleep(30)  # 30초 간격

    return StreamingResponse(ping_stream(), media_type="text/event-stream")

#기본대화모드?
@router.post("/{chatroom_id}/messages", description="기본대화 모드?" ,tags=["Chat"])
async def ask_ai(chatroom_id: int, user_input: UserInput):
    """
    사용자 입력을 기반으로 Claude API 호출 후,
    응답을 SSE 방식으로 스트리밍하며 음성 데이터를 포함
    """
    async def event_stream():
        try:
            for emotion in user_input.emotions:
                try:
                    logging.info(f"Processing emotion: {emotion}")

                    system_prompt = f"{emotion}: {PROMPTS[emotion]}"
                    full_prompt = f"{RULES}\n\n사용자: {user_input.prompt}\n"

                    with client.messages.stream(
                        max_tokens=600,
                        system=system_prompt,
                        messages=[{"role": "user", "content": full_prompt}],
                        model="claude-3-5-haiku-20241022",
                    ) as stream:
                        buffer = []  
                        chunk_size = 3  # 버퍼에 누적할 Claude응답 청크 개수 조절

                        async for text in async_wrap(stream.text_stream):
                            buffer.append(text) 
                            if len(buffer) >= chunk_size: 
                                combined_text = ' '.join(buffer) 
                                buffer = []

                                # 텍스트->음성 변환
                                voice_id = emotion_to_voice_id.get(emotion, "Es5AnE58gKPS9Vffyooe") #뒤 이상한 코드는 매핑기본값
                                audio_stream = text_to_speech_stream(combined_text, voice_id)

                                # 음성데이터 Base64로 인코딩
                                audio_base64 = base64.b64encode(audio_stream.getvalue()).decode("utf-8")

                                # 클라이언트로 전송할 데이터(json)
                                data = {
                                    "type": "content_chunk",
                                    "emotion": emotion,
                                    "content": combined_text,
                                    "audio": audio_base64,
                                }
                                yield f"data: {json.dumps(data)}\n\n"
                                await asyncio.sleep(0.1)

                        if buffer:  # 버퍼에 남아 있는 청크가 없도록 끝까지 처리
                            combined_text = ' '.join(buffer)
                            voice_id = emotion_to_voice_id.get(emotion, "Es5AnE58gKPS9Vffyooe")
                            audio_stream = text_to_speech_stream(combined_text, voice_id)
                            audio_base64 = base64.b64encode(audio_stream.getvalue()).decode("utf-8")
                            data = {
                                "type": "content_chunk",
                                "emotion": emotion,
                                "content": combined_text,
                                "audio": audio_base64,
                            }
                            yield f"data: {json.dumps(data)}\n\n"

                except Exception as inner_error:
                    # 개별 감정 처리 중 에러 발생 시
                    logging.error(f"Error processing emotion {emotion}: {inner_error}")
                    error_data = {
                        "type": "error",
                        "emotion": emotion,
                        "message": str(inner_error),
                    }
                    yield f"data: {json.dumps(error_data)}\n\n"

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


async def async_wrap(generator):
    for item in generator:
        yield item




#보고서 생성
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