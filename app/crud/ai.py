import anthropic
import os

# .env에서 API 키 가져옴
api_key = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=api_key)

def get_ai_response(prompt: str) -> str:

    try:
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=300,
            temperature=0.7,
            system="너는 공감적이고 현명한 감정조언자다. 너의 임무는 다양한 감정적 상황이나 딜레마에 직면한 사용자에게 3문장 이내로 사려 깊은 조언을 제공해.\n"
                   "너는 인사이드아웃 영화에 나오는 기쁨이, 슬픔이, 버럭이, 까칠이, 소심이, 불안이, 당황이 이렇게 7가지 감정의 각각의 입장에서 사용자에게 조언을 제공해.",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        return response.content

    except Exception as e:
        return f"Error: {str(e)}"