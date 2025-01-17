from sqlalchemy.orm import Session
from models import EmotionChoose

def create_emotion_chooses(db: Session, chatroom_id: int, emotion_ids: list[int]) -> list[int]:
    emotion_choose_ids = []
    for emotion_id in emotion_ids:
        emotion_choose = EmotionChoose(chatroom_id=chatroom_id, emotion_id=emotion_id)
        db.add(emotion_choose)
        db.commit()
        db.refresh(emotion_choose)
        emotion_choose_ids.append(emotion_choose.id)
    return emotion_choose_ids