from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from models import Emotion
from datetime import datetime
import pytz
import os
from sqlalchemy.pool import StaticPool

if os.getenv("TESTING") == "True":
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(os.getenv('MYSQL_DATABASE_URL'))

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
            Emotion(
                emotion_name="기쁨이",
                explanation="기분이 좋은 상태",
                wording="어려운 점만 계속 신경쓸 수는 없어. 상황을 바꿀 수 있는 방법은 항상 있지. 즐거움을 찾는 거 말야!",
                is_deleted=False,
                created_at=datetime.now(KST),
                updated_at=datetime.now(KST)
            ),

            #슬픔이 2
            Emotion(
                emotion_name="슬픔이",
                explanation="마음이 아프거나 슬픈 상태",
                wording="때로는 슬퍼도 괜찮아, 슬픔을 느끼는 건 네가 무언가를 소중히 여긴다는 뜻이야.",
                is_deleted=False,
                created_at=datetime.now(KST),
                updated_at=datetime.now(KST)
            ),
            #버럭이 3
            Emotion(
                emotion_name="버럭이",
                explanation="화가난 상태",
                wording="너는 많은 실수를 했고 앞으로도 더 많이 하겠지. 그렇다고 멈춘다면 여기서 결국 주저앉아 포기하게 될거야",
                is_deleted=False,
                created_at=datetime.now(KST),
                updated_at=datetime.now(KST)
            ),
            #까칠이 4
            Emotion(
                emotion_name="까칠이",
                explanation="까칠한 상태",
                wording="네 직감을 믿어. 그것들은 결코 거짓말 하지 않아.",
                is_deleted=False,
                created_at=datetime.now(KST),
                updated_at=datetime.now(KST)
            ),
            #소심이 5
            Emotion(
                emotion_name="소심이",
                explanation="소심한 상태",
                wording="변화는 두렵지만, 때론 위대한 일로 이어지기도 해.",
                is_deleted=False,
                created_at=datetime.now(KST),
                updated_at=datetime.now(KST)
            ),
            #불안이 6
            Emotion(
                emotion_name="불안이",
                explanation="불안한 상태",
                wording="우리에겐 다양한 감정이 섞여 있어. 그게 우리를 독특하고 아름답게 만들지.",
                is_deleted=False,
                created_at=datetime.now(KST),
                updated_at=datetime.now(KST)
            ),
            #당황이 7
            Emotion(
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

def clear_db():
    meta = MetaData()
    meta.reflect(bind=engine)
    with engine.connect() as conn:
        for table in reversed(meta.sorted_tables):
                conn.execute(table.delete())
        conn.commit()