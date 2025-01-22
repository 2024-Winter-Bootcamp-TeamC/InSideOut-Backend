from io import BytesIO
import base64
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import os

# 환경 변수에서 ElevenLabs API 키 가져오기
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
tts_client = ElevenLabs(api_key=elevenlabs_api_key)

# 감정별 음성 ID 매핑
emotion_to_voice_id = {
    "기쁨이": "Psd3Dws300YDo1OOqO0U",
    "슬픔이": "TwDb4GqeH0gVSbvXGv2S",
    "버럭이": "LbFHNL6b2OeZR8dGzyaO",
    "까칠이": "vT7e4zoYComik9uh2AHK",
    "소심이": "Tr2VDPdFpJGUJx63YVMQ",
    "불안이": "fHDolfOtF6CpYTE7oWUM",
    "당황이": "Ntxene0wnChhqSVUN483",
}

def text_to_speech_stream(text: str, voice_id: str) -> BytesIO:
    """
    ElevenLabs TTS API를 사용하여 텍스트를 음성으로 변환하고,
    BytesIO 스트림 형태로 반환합니다.
    """
    response = tts_client.text_to_speech.convert(
        voice_id=voice_id,
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings=VoiceSettings(
            stability=0.3,
            similarity_boost=1.0,
            style=0.5,
            use_speaker_boost=True,
        ),
    )
    audio_stream = BytesIO()
    for chunk in response:
        if chunk:
            audio_stream.write(chunk)
    audio_stream.seek(0)
    return audio_stream
