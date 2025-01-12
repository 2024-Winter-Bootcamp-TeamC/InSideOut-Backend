from sqlalchemy import Column, Integer, String, Boolean,DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pytz

# 기본 클래스 생성
Base = declarative_base()
KST = pytz.timezone("Asia/Seoul")
# 테이블 매핑
class User(Base):
    __tablename__ = 'users'  # 테이블 이름

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String(10), nullable=False)
    password = Column(String(20), unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(KST))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(KST),
        onupdate=lambda: datetime.now(KST),
    )
    is_deleted = Column(Boolean, default=False)


