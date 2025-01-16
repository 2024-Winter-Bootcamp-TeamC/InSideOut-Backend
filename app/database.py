from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models import Emotions
from datetime import datetime
import pytz

engine = create_engine('mysql+pymysql://root:root@insideout-backend-teamC_mysql-1:3306/InsideOut')
meta = MetaData()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

KST = pytz.timezone("Asia/Seoul")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def initialize_database():
    db = SessionLocal()
    try:
        # 초기 감정 데이터
        emotions = [
            #기쁨이 1
            Emotions(
                emotion_name="기쁨이",
                explanation="기분이 좋은 상태",
                wording="기쁨이 명대사",
                is_deleted=False,
                created_at=datetime.now(KST),
                updated_at=datetime.now(KST)
            ),
            #슬픔이 2
            Emotions(
                emotion_name="슬픔이",
                explanation="마음이 아프거나 슬픈 상태",
                wording="슬픔이 명대사",
                is_deleted=False,
                created_at=datetime.now(KST),
                updated_at=datetime.now(KST)
            ),
            #버럭이 3
            Emotions(
                emotion_name="버럭이",
                explanation="화가난 상태",
                wording="버럭이 명대사",
                is_deleted=False,
                created_at=datetime.now(KST),
                updated_at=datetime.now(KST)
            ),
            #까칠이 4
            Emotions(
                emotion_name="까칠이",
                explanation="까칠한 상태",
                wording="까칠이이 명대사",
                is_deleted=False,
                created_at=datetime.now(KST),
                updated_at=datetime.now(KST)
            ),
            #소심이 5
            Emotions(
                emotion_name="소심이",
                explanation="소심한 상태",
                wording="소심이 명대사",
                is_deleted=False,
                created_at=datetime.now(KST),
                updated_at=datetime.now(KST)
            ),
            #불안이 6
            Emotions(
                emotion_name="불안이",
                explanation="불안한 상태",
                wording="불안이 명대사",
                is_deleted=False,
                created_at=datetime.now(KST),
                updated_at=datetime.now(KST)
            ),
            #당황이 7
            Emotions(
                emotion_name="당황이",
                explanation="당황한 상태",
                wording="당황이 명대사",
                is_deleted=False,
                created_at=datetime.now(KST),
                updated_at=datetime.now(KST)
            ),
        ]
        # 데이터 삽입
        db.bulk_save_objects(emotions)
        db.commit()
    finally:
        db.close()

