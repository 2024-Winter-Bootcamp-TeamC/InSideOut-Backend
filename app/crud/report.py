from models import Report,EmotionPercentages,Emotions  # Report는 SQLAlchemy 모델
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
import json

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

    # 카테고리와 상황요약은 Redis 만들어지면 구현
    category="Redis" 
    situation_summary="Redis 만들어지면 구현"

    #JSON 형태로 받음
    all_emotion_summary = {"기쁨이":"나는 기뻐","슬픔이":"나는 슬퍼", "버럭이":"나는 화나"}
    all_emotion_percentage ={"기쁨이":19.8,"슬픔이":60.1, "버럭이":20.1}
    

    response_data = Report(
        user_id=user_id,
        title=datetime.now().strftime("%Y-%m-%d"),
        situation_summary=situation_summary,
        emotion_summary=all_emotion_summary,
        category=category
    )

    # DB에 추가
    db.add(response_data)
    db.commit() 
    db.refresh(response_data)

    parse_percentages(all_emotion_percentage, response_data.id, db)

    return response_data.id

def parse_percentages(all_emotion_percentage: dict, report_id: int, db: Session):
    # 감정 이름과 아이디 매핑
    emotion_map = {
        "기쁨이": 1,
        "슬픔이": 2,
        "버럭이": 3,
        "까칠이": 4,
        "소심이": 5,
        "불안이": 6,
        "당황이": 7
    }

    #JSON형태의 감정이름:퍼센테이지를 파싱해서 데이터베이스에 저장
    for emotion_name, percentage in all_emotion_percentage.items():
        if emotion_name in emotion_map:
            emotion_id = emotion_map[emotion_name]
            try:
                percentage_value = float(percentage)
                
                emotion_percentage_entry = EmotionPercentages(
                    report_id=report_id,
                    emotion_id=emotion_id,
                    percentages=percentage_value
                )

                db.add(emotion_percentage_entry)
            except ValueError:
                # 퍼센티지 변환 실패 시 처리
                raise HTTPException(status_code=400, detail=f"Invalid percentage value for {emotion_name}")

    # DB에 변경사항 커밋
    db.commit()



def get_report_by_report_id(report_id: int, db: Session):
   
    report_data = db.query(Report).filter(Report.id == report_id, Report.is_deleted == False).first()

    emotion_data = db.query(EmotionPercentages.emotion_id, EmotionPercentages.percentages) \
        .filter(EmotionPercentages.report_id == report_id, EmotionPercentages.is_deleted == False) \
        .all()

    max_percentage = max(emotion_data, key=lambda x: x[1]) if emotion_data else (None, 0)
    max_emotion_id = max_percentage[0] if max_percentage else None

    wording_data = db.query(Emotions.wording) \
        .filter(Emotions.id == max_emotion_id, Emotions.is_deleted == False) \
        .first()

    emotions_percentage = {str(e[0]): e[1] for e in emotion_data}

    # 반환할 데이터를 하나의 딕셔너리로 묶기
    return {
        "title": report_data.title if report_data else "",
        "situation_summary": report_data.situation_summary if report_data else "",
        "emotion_summary": report_data.emotion_summary if report_data else {},
        "wording": wording_data.wording if wording_data else "",
        "emotion_percentage": emotions_percentage  
    }
    