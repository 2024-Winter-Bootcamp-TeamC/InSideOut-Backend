from typing import List, Optional
from sqlalchemy.orm import Session
import asyncio
import json
import base64
from crud.preparation import redis_client
from utils.tts import text_to_speech_stream, emotion_to_voice_id
from utils.prompt import PROMPTS, RULES, DEBATE_PROMPTS, BASIC_PROMPTS
from elevenlabs.client import ElevenLabs
import anthropic
import os
from models import Chat
from elevenlabs import VoiceSettings
api_key = os.getenv("ANTHROPIC_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
client = anthropic.Anthropic(api_key=api_key)
tts_client = ElevenLabs(api_key=elevenlabs_api_key)
emotion_to_voice_settings = {
    "기쁨이": VoiceSettings(stability=0.5, similarity_boost=0.9, style=0.6, use_speaker_boost=True),
    "슬픔이": VoiceSettings(stability=0.5, similarity_boost=0.8, style=0.3, use_speaker_boost=True),
    "버럭이": VoiceSettings(stability=0.5, similarity_boost=0.8, style=0.3, use_speaker_boost=True),
    "까칠이": VoiceSettings(stability=0.4, similarity_boost=0.8, style=0.5, use_speaker_boost=True),
    "소심이": VoiceSettings(stability=0.5, similarity_boost=0.8, style=0.0, use_speaker_boost=True),
    "불안이": VoiceSettings(stability=0.4, similarity_boost=0.8, style=0.4, use_speaker_boost=True),
    "부럽이": VoiceSettings(stability=0.5, similarity_boost=0.8, style=0.0, use_speaker_boost=True),
}
async def async_wrap(generator):
    for item in generator:
        yield item
async def generate_event_stream(
    user_id: int,
    chatroom_id: int,
    emotions: List[str],
    db: Session,
    mode: str,
    user_prompt: Optional[str] = None
):
    try:
        total_chat_buffer = ""
        for iteration in range(3 if mode == "discussions" else 1):
            for emotion in emotions:
                try:
                    preparation = await redis_client.get(f"user_{user_id}")
                    before_chat = await redis_client.get(f"chat_{chatroom_id}")
                    before_user_input = await redis_client.get(f"chat_user_input_{chatroom_id}")
                    chat_buffer = f"{emotion} : "
                    system_prompt = f"{emotion}: {PROMPTS[emotion]}"
                    full_prompt = create_full_prompt(
                        mode, emotion, preparation, before_chat,before_user_input,iteration,user_prompt
                    )
                    with client.messages.stream(
                        max_tokens=150,
                        system=system_prompt,
                        temperature=0.5,
                        messages=[{"role": "user", "content": full_prompt}],
                        model="claude-3-5-sonnet-20241022",
                    ) as stream:
                        buffer = []
                        chunk_size = 6
                        async for text in async_wrap(stream.text_stream):
                            chat_buffer += text
                            buffer.append(text)
                            if len(buffer) >= chunk_size:
                                combined_text = ''.join(buffer)
                                buffer = []
                                voice_id = emotion_to_voice_id.get(emotion, "Es5AnE58gKPS9Vffyooe")
                                audio_stream = text_to_speech_stream(combined_text, voice_id, emotion_to_voice_settings[emotion])
                                audio_base64 = base64.b64encode(audio_stream.getvalue()).decode("utf-8")
                                data = {
                                    "type": "content_chunk",
                                    "emotion": emotion,
                                    "content": combined_text,
                                    "audio": audio_base64,
                                    "iteration": iteration,
                                }
                                yield f"data: {json.dumps(data)}\n\n"
                                await asyncio.sleep(0)
                        if buffer:
                            combined_text = ''.join(buffer)
                            voice_id = emotion_to_voice_id.get(emotion, "Es5AnE58gKPS9Vffyooe")
                            audio_stream = text_to_speech_stream(combined_text, voice_id,emotion_to_voice_settings[emotion])
                            audio_base64 = base64.b64encode(audio_stream.getvalue()).decode("utf-8")
                            data = {
                                "type": "content_chunk",
                                "emotion": emotion,
                                "content": combined_text,
                                "audio": audio_base64,
                                "iteration": iteration,
                            }
                            yield f"data: {json.dumps(data)}\n\n"
                        total_chat_buffer += chat_buffer + "\n"
                        await redis_client.append(
                        f"chat_{chatroom_id}",
                        json.dumps(total_chat_buffer, ensure_ascii=False).encode("utf-8"),
                        )
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
        if mode == "messages":
            await redis_client.append(
                f"chat_user_input_{chatroom_id}",
                json.dumps({"user_input": user_prompt}, ensure_ascii=False).encode("utf-8"),
            )
def create_full_prompt(mode: str, emotion: str, preparation: str, before_chat: str,before_user_input:str,iteration:int,user_prompt:str) -> str:
    """Create a full prompt based on mode and input."""
    if mode == "messages":
        return f"""
        {RULES}\n
        사용자 고민내용: {preparation}
        기본모드: {BASIC_PROMPTS}
        사용자 입력: {user_prompt}
        이전 대화 내용: {before_chat}
        이전 사용자 입력: {before_user_input}
        """
    elif mode == "discussions":
        return f"""
        {RULES}\n
        사용자 고민내용: {preparation}
        논쟁모드: {DEBATE_PROMPTS}
        이전 대화 내용: {before_chat}
        이전 사용자 입력: {before_user_input}
        사이클: "{iteration+1}번쨰 사이클"
        """
    else:
        raise ValueError("Invalid mode")
    

def save_chat(client_message, emotion_message, chatroom_id, db):

    # 유저 메시지 저장
    response_data = Chat(
        chatroom_id=chatroom_id,
        chat_content=client_message,
        chat_speaker="client"  
    )
    db.add(response_data)
    db.commit()
    db.refresh(response_data)

    # 감정 메시지 저장
    response_data = Chat(
        chatroom_id=chatroom_id,
        chat_content=emotion_message,
        chat_speaker="emotions"  
    )
    db.add(response_data)
    db.commit()
    db.refresh(response_data)