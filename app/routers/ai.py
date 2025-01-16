# app/routers/ai.py
from fastapi import APIRouter, HTTPException
from crud.ai import get_ai_responses
from pydantic import BaseModel
from typing import List

router = APIRouter()

class AIRequest(BaseModel):
    prompt: str
    emotions: List[str]

@router.post("/ask-ai")
def ask_ai(request: AIRequest):
    """
    사용자의 질문을 받아 클로드 AI에 전달하고 응답을 반환하는 엔드포인트
    """
    try:
        response = get_ai_responses(prompt=request.prompt, emotions=request.emotions)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
