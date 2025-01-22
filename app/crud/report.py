from models import Report,EmotionPercentage,Emotion  # Report는 SQLAlchemy 모델
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from crud.chatroom import delete_chatroom
from crud.ai import create_report
from crud.preparation import redis_client
from crud.chat import save_chat
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

async def post_report_by_user_id(user_id: int, chatroom_id: int, db: Session):

    category_key = f"category_{user_id}"
    content_key = f"content_{user_id}"
    chat_key = f"chat_{chatroom_id}"
    chat_user_input_key = f"chat_user_input_{chatroom_id}"

    # Redis에서 값 가져오기
    category = await redis_client.get(category_key)
    situation_summary = await redis_client.get(content_key)
    client_message = await redis_client.get(chat_user_input_key)
    emotion_message = await redis_client.get(chat_key)
    
    if not client_message or not emotion_message:
        raise HTTPException(status_code=400, detail="Invalid input data from Redis.")

    # Redis에서 가져온 값 삭제
    await redis_client.delete(category_key)
    await redis_client.delete(content_key)
    await redis_client.delete(chat_key)
    await redis_client.delete(chat_user_input_key)

    save_chat(client_message, emotion_message, chatroom_id, db)
    all_emotion_percentage, all_emotion_summary = create_report(client_message, emotion_message)

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

    delete_chatroom(db, chatroom_id)

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
                
                emotion_percentage_entry = EmotionPercentage(
                    report_id=report_id,
                    emotion_id=emotion_id,
                    percentages=percentage_value
                )

                db.add(emotion_percentage_entry)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid percentage value for {emotion_name}")

    db.commit()



def get_report_by_report_id(report_id: int,  db: Session):
    report_data = db.query(Report).filter(Report.id == report_id, Report.is_deleted == False).first()
    
    if not report_data or report_data.is_deleted:
        raise HTTPException(status_code=400, detail="Report already deleted")
    
    emotion_data = db.query(EmotionPercentage.emotion_id, EmotionPercentage.percentages) \
        .filter(EmotionPercentage.report_id == report_id, EmotionPercentage.is_deleted == False) \
        .all()

    max_percentage = max(emotion_data, key=lambda x: x[1]) if emotion_data else (None, 0)
    max_emotion_id = max_percentage[0] if max_percentage else None

    wording = db.query(Emotion.emotion_name, Emotion.wording) \
        .filter(Emotion.id == max_emotion_id, Emotion.is_deleted == False) \
        .first()

    Emotion_percentage = {str(e[0]): e[1] for e in emotion_data}
    wording_data={str(wording[0]):str(wording[1])}

    # 반환할 데이터를 하나의 딕셔너리로 묶기
    return {
        "title": report_data.title if report_data else "",
        "situation_summary": report_data.situation_summary if report_data else "",
        "emotion_summary": report_data.emotion_summary if report_data else {},
        "wording": wording_data if wording_data else "",
        "emotion_percentage": Emotion_percentage  
    }

def delete_report_by_report_id(report_id: int, db: Session):
    report = db.query(Report).filter(Report.id == report_id).first()
    emotion_percentages=db.query(EmotionPercentage).filter(EmotionPercentage.report_id == report_id).all()

    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.is_deleted:
        raise HTTPException(status_code=400, detail="Report already deleted")
    if not emotion_percentages:
        raise HTTPException(status_code=404, detail="Emotion percentages not found")
    

    report.is_deleted = True
    report.updated_at = datetime.now()
    
    for emotion_percentage in emotion_percentages:
        emotion_percentage.is_deleted = True
        emotion_percentage.updated_at = datetime.now()

    db.commit()

    return {"status": "success", "message": "Report deleted successfully"}
