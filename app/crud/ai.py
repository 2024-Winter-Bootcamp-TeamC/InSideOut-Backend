import anthropic
import os
import json
from typing import List
from utils.prompt import REPORT_PROMPTS

api_key = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=api_key)

def create_report(client_message: List[str], emotion_message: List[str]):
    """
    사용자 입력 메시지와 감정 데이터를 바탕으로 Claude AI에 요청을 보내고,
    감정 퍼센티지와 감정별 요약을 생성합니다.
    """
    full_prompt = f"""
    사용자 메시지: {client_message}
    감정 메시지: {emotion_message}
    규칙 : {REPORT_PROMPTS}
    """
    try:
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1000,
            temperature=0.0,  
            messages=[{"role": "user", "content": full_prompt}]
        )
        response_text = response.content[0].text.strip()  

        if '###' not in response_text:
            raise ValueError("Unexpected response format: '###' separator not found.")

        percentages_text, summaries_text = response_text.split('###', 1)

        response_percentages = json.loads(percentages_text)
        response_summary = json.loads(summaries_text)

        return {
            "response_percentages": response_percentages,
            "response_summary": response_summary,
        }

    except json.JSONDecodeError as decode_error:
        return {"error": f"JSON decode error: {decode_error}"}
    except Exception as e:
        return {"error": str(e)}