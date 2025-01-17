# app/routers/ai.py
from fastapi import APIRouter, HTTPException
from crud.ai import get_ai_responses, create_report
from pydantic import BaseModel
from typing import List, Dict

router = APIRouter()

class AIRequest(BaseModel):
    prompt: str
    emotions: List[str]

class createRequest(BaseModel):
    client_message: List[str]  
    emotion_message: Dict[str, List[str]]


@router.post("/ask-ai", tags=["AI"])
def ask_ai(request: AIRequest):
    """
    사용자의 질문을 받아 클로드 AI에 전달하고 응답을 반환하는 엔드포인트
    """
    try:
        response = get_ai_responses(prompt=request.prompt, emotions=request.emotions)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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