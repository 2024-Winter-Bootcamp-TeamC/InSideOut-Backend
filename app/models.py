from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import pytz

# 기본 클래스 생성
Base = declarative_base()
KST = pytz.timezone("Asia/Seoul")

# 테이블 매핑
class User(Base):
    __tablename__ = 'users'  # 테이블 이름

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String(10), nullable=False, unique=True)
    password = Column(String(20), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(KST))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(KST),
        onupdate=lambda: datetime.now(KST),
    )
    is_deleted = Column(Boolean, default=False)

    reports = relationship("Report", back_populates="user")
    chatrooms = relationship("Chatroom", back_populates="user")


class Report(Base):
    __tablename__ = 'reports'  # 테이블 이름

    id = Column(Integer, primary_key=True, index=True)  # 기본 키
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 외래 키
    title = Column(String(20), nullable=False) 
    situation_summary = Column(Text, nullable=False)  
    emotion_summary = Column(Text, nullable=False)  
    category = Column(String(10), nullable=False)  
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(KST))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(KST),
        onupdate=lambda: datetime.now(KST),  
    )
    is_deleted = Column(Boolean, default=False) 

    # 외래 키 관계 설정
    user = relationship("User", back_populates="reports")


class Emotion(Base):
    __tablename__ = "emotions"

    id = Column(Integer, primary_key=True)
    emotion_name = Column(String(10), nullable=False)
    explanation = Column(String(100), nullable=False) 
    is_deleted = Column(Boolean, nullable=False, default=False) 
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(KST))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(KST), onupdate=lambda: datetime.now(KST))

    emotion_choices = relationship("EmotionChoose", back_populates="emotion")


class Chatroom(Base):
    __tablename__ = "chatrooms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  
    update_report_id = Column(Integer, nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(KST))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(KST), onupdate=lambda: datetime.now(KST))
    

    # 관계 설정
    user = relationship("User", back_populates="chatrooms")
    emotion_choices = relationship("EmotionChoose", back_populates="chatroom")


class EmotionChoose(Base):
    __tablename__ = "emotionchoose"

    id = Column(Integer, primary_key=True)
    chatroom_id = Column(Integer, ForeignKey("chatrooms.id"), nullable=False)  # 채팅방 ID
    emotion_id = Column(Integer, ForeignKey("emotions.id"), nullable=False)  # 선택된 감정 ID
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(KST))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(KST), onupdate=lambda: datetime.now(KST))

    # 관계 설정
    chatroom = relationship("Chatroom", back_populates="emotion_choices")
    emotion = relationship("Emotion", back_populates="emotion_choices")
