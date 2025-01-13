# app/routers/ai.py
from fastapi import APIRouter, HTTPException
from crud.ai import get_ai_response  # crud/ai.py의 함수 호출

router = APIRouter()

@router.post("/ask-ai")
def ask_ai(prompt: str):
    """
    사용자의 질문을 받아 클로드 AI에 전달하고 응답을 반환하는 엔드포인트
    """
    try:
        response = get_ai_response(prompt)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
