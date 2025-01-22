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

api_key = os.getenv("ANTHROPIC_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")

client = anthropic.Anthropic(api_key=api_key)
tts_client = ElevenLabs(api_key=elevenlabs_api_key)

async def async_wrap(generator):
    for item in generator:
        yield item


async def generate_event_stream(
    user_id: int, 
    chatroom_id: int, 
    emotions: List[str], 
    db: Session, 
    mode: str,
    user_prompt: Optional[str] | None
):
    try:
        total_chat_buffer = ""
        for iteration in range(3 if mode == "discussions" else 1):  
            for emotion in emotions:
                try:
                    preparation = await redis_client.get(f"user_{user_id}")
                    before_chat = await redis_client.get(f"chat_{chatroom_id}")
                    chat_buffer = f"{emotion} : "
                    system_prompt = f"{emotion}: {PROMPTS[emotion]}"
                    full_prompt = create_full_prompt(
                        mode, emotion, preparation, before_chat
                    )

                    with client.messages.stream(
                        max_tokens=150,
                        system=system_prompt,
                        messages=[{"role": "user", "content": full_prompt}],
                        model="claude-3-5-haiku-20241022",
                    ) as stream:
                        buffer = []
                        chunk_size = 4

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

                        total_chat_buffer += chat_buffer + "\n"

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
        await redis_client.append(
            f"chat_{chatroom_id}",
            json.dumps({"total_chat_buffer": total_chat_buffer}, ensure_ascii=False).encode("utf-8"),
        )
        if mode == "messages":
            await redis_client.append(
                f"chat_user_input_{chatroom_id}",
                json.dumps({"user_input": user_prompt}, ensure_ascii=False).encode("utf-8"),
            )


def create_full_prompt(mode: str, emotion: str, preparation: str, before_chat: str) -> str:
    """Create a full prompt based on mode and input."""
    if mode == "messages":
        return f"""
        {RULES}\n
        사용자 고민내용: {preparation}
        기본모드: {BASIC_PROMPTS}
        이전 대화 내용: {before_chat}
        """
    elif mode == "discussions":
        return f"""
        {RULES}\n
        사용자 고민내용: {preparation}
        논쟁모드: {DEBATE_PROMPTS}
        이전 대화 내용: {before_chat}
        """
    else:
        raise ValueError("Invalid mode")