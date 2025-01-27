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
    "기쁨이": "pxgp3pP2SHK7HCM39UHr",
    "슬픔이": "pKWkfu98pcmm4MK6UJVv",
    "버럭이": "1qGwpjRoDOuE1Rg5OEnX",
    "까칠이": "qXIbfegjOFo3nSkqbpkt",
    "소심이": "TwmwwkgldIUpfl12d37c",
    "불안이": "o7U3fscjBBeMxpgYryjE",
    "부럽이": "m4GqDqLkoDhAK8hKzngg",
}
# 감정별 VoiceSettings 매핑
emotion_to_voice_settings = {
    "기쁨이": VoiceSettings(stability=0.5, similarity_boost=0.9, style=0.6, use_speaker_boost=True),
    "슬픔이": VoiceSettings(stability=0.5, similarity_boost=0.8, style=0.3, use_speaker_boost=True),
    "버럭이": VoiceSettings(stability=0.5, similarity_boost=0.8, style=0.3, use_speaker_boost=True),
    "까칠이": VoiceSettings(stability=0.4, similarity_boost=0.8, style=0.5, use_speaker_boost=True),
    "소심이": VoiceSettings(stability=0.5, similarity_boost=0.8, style=0.0, use_speaker_boost=True),
    "불안이": VoiceSettings(stability=0.4, similarity_boost=0.8, style=0.4, use_speaker_boost=True),
    "부럽이": VoiceSettings(stability=0.5, similarity_boost=0.8, style=0.0, use_speaker_boost=True),
}
def text_to_speech_stream(text: str, voice_id: str, voice_settings: VoiceSettings) -> BytesIO:
    """
    ElevenLabs TTS API를 사용하여 텍스트를 음성으로 변환하고,
    BytesIO 스트림 형태로 반환합니다.
    """
    response = tts_client.text_to_speech.convert(
        voice_id=voice_id,
        voice_settings=voice_settings,
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2",
    )
    audio_stream = BytesIO()
    for chunk in response:
        if chunk:
            audio_stream.write(chunk)
    audio_stream.seek(0)
    return audio_stream