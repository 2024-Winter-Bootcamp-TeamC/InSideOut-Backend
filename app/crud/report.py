from models import Report
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

def get_ai_response(prompt: str) -> dict:
    """
    openai.api_key = "YOUR_API_KEY"
    response = openai.Completion.create(
        model="text-davinci-003",  # 모델을 선택합니다.
        prompt=prompt,
        max_tokens=150  # 답변 길이 제한
    )
    """
    return "안녕하세요/반갑습니다/고맙습니다"

def get_reports_by_user_id(user_id: int, db: Session):
    reports = db.query(Report).filter(Report.user_id == user_id, Report.is_deleted == False).all()
    
    if not reports:
        raise HTTPException(status_code=404, detail="No data was found.")
    
    report_list = []
    for report in reports:
        report_list.append({
            "report_id": report.id,
            "category": report.category,
            "title": report.title
        })

    return report_list


def post_report_by_user_id(user_id: int, db: Session):
    prompt = "사용자의 상황 요약과 감정 요약을 제공합니다."
    ai_response = get_ai_response(prompt)

    category,situation_summary, emotion_summary = ai_response.split("/")  # 구분자 /

    report = Report(
        user_id=user_id,
        category=category,
        title=datetime.now().strftime("%Y-%m-%d"),
        situation_summary=situation_summary,
        emotion_summary=emotion_summary
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return report.id