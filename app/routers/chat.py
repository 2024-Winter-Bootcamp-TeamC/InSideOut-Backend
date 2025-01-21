# app/routers/chat.py
from fastapi import APIRouter, HTTPException, Depends
from utils.prompt import PROMPTS, RULES,DEBATE_PROMPTS,BASIC_PROMPTS
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
from schemas.report import createReportRequest
from crud.preparation import redis_client
from crud.ai import create_report
from schemas.chat import UserInput, Discussion
from database import get_db
from sqlalchemy.orm import Session
from crud.ai import ValidateUserandChatRoom

router = APIRouter()

api_key = os.getenv("ANTHROPIC_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")

client = anthropic.Anthropic(api_key=api_key)
tts_client = ElevenLabs(api_key=elevenlabs_api_key)

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


@router.post("/{chatroom_id}/messages", description="기본대화 모드?" ,tags=["Chat"])
async def ask_ai(chatroom_id: int,user_id:int, user_input: UserInput,db: Session = Depends(get_db)):
    """
    사용자 입력을 기반으로 Claude API 호출 후,
    응답을 SSE 방식으로 스트리밍하며 음성 데이터를 포함
    """
    ValidateUserandChatRoom(user_id, chatroom_id,db)
    preparation = await redis_client.get(f"user_{user_id}")
    before_chat = await redis_client.get(f"chat_{chatroom_id}")
    async def event_stream():
        try:
            total_chat_buffer = ""  
        
            for emotion in user_input.emotions:
                try:
                    chat_buffer = f"{emotion} : "
                    system_prompt = f"{emotion}: {PROMPTS[emotion]}"
                    full_prompt = f"""
                    {RULES}\n
                    사용자: {user_input.prompt} 
                    사용자 고민내용:{preparation}
                    기본모드: {BASIC_PROMPTS}
                    이전 대화 내용:{before_chat}
                    """

                    with client.messages.stream(
                        max_tokens=150,
                        system=system_prompt,
                        messages=[{"role": "user", "content": full_prompt}],
                        model="claude-3-5-haiku-20241022",
                    ) as stream:
                        buffer = []
                        chunk_size = 6

                        async for text in async_wrap(stream.text_stream):
                            chat_buffer += text
                            buffer.append(text)
                            if len(buffer) >= chunk_size:
                                combined_text = ' '.join(buffer)
                                buffer = []

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
                                await asyncio.sleep(0)


                        if buffer:
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
                        total_chat_buffer += chat_buffer + "\n"  # 모든 감정 데이터 누적

                except Exception as inner_error:

                    error_data = {
                        "type": "error",
                        "emotion": emotion,
                        "message": str(inner_error),
                    }
                    yield f"data: {json.dumps(error_data)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            
        finally:
            await redis_client.set(f"chat_{chatroom_id}", json.dumps({total_chat_buffer},ensure_ascii=False).encode('utf-8'))
            await redis_client.set(f"chat_user_input_{user_id}", json.dumps({user_input.prompt},ensure_ascii=False).encode('utf-8'))
        

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@router.post("/{chatroom_id}/discussions", description="기본대화 모드?" ,tags=["Chat"])
async def ask_ai(chatroom_id: int, user_id:int, discuss: Discussion,db: Session = Depends(get_db)):
    """
    사용자 입력을 기반으로 Claude API 호출 후,
    응답을 SSE 방식으로 스트리밍하며 음성 데이터를 포함
    """
    ValidateUserandChatRoom(user_id, chatroom_id,db)
    async def event_stream():
        try:
            total_chat_buffer = ""  
            for iteration in range(3):
                for emotion in discuss.emotions:
                    try:
                        preparation = await redis_client.get(f"user_{user_id}")
                        before_chat = await redis_client.get(f"chat_{chatroom_id}")
                        chat_buffer = f"{emotion} : "
                        system_prompt = f"{emotion}: {PROMPTS[emotion]}"
                        full_prompt = f"""
                        {RULES}\n
                        사용자 고민내용:{preparation}
                        논쟁모드: {DEBATE_PROMPTS}
                        이전 대화 내용:{before_chat}
                        """

                        with client.messages.stream(
                            max_tokens=150,
                            system=system_prompt,
                            messages=[{"role": "user", "content": full_prompt}],
                            model="claude-3-5-haiku-20241022",
                        ) as stream:
                            buffer = []
                            chunk_size = 6

                            async for text in async_wrap(stream.text_stream):
                                chat_buffer += text
                                buffer.append(text)
                                if len(buffer) >= chunk_size:
                                    combined_text = ' '.join(buffer)
                                    buffer = []

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
                                    await asyncio.sleep(0)


                            if buffer:
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
                            total_chat_buffer += chat_buffer + "\n"  # 모든 감정 데이터 누적

                    except Exception as inner_error:

                        error_data = {
                            "type": "error",
                            "emotion": emotion,
                            "message": str(inner_error),
                        }
                        yield f"data: {json.dumps(error_data)}\n\n"

        except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                
        finally:
                await redis_client.set(f"chat_{chatroom_id}", json.dumps({total_chat_buffer},ensure_ascii=False).encode('utf-8'))
            
        

    return StreamingResponse(event_stream(), media_type="text/event-stream")


async def async_wrap(generator):
    for item in generator:
        yield item




#보고서 생성
@router.post("/report-ai", tags=["AI"])
def report(request: createReportRequest ):
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