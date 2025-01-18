from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import pytz

# 기본 클래스 생성
Base = declarative_base()
KST = pytz.timezone("Asia/Seoul")

# 테이블 매핑
class User(Base):
    __tablename__ = 'user'  # 테이블 이름
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
    __tablename__ = 'report'  # 테이블 이름

    id = Column(Integer, primary_key=True, index=True)  # 기본 키
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)  # 외래 키
    title = Column(String(20), nullable=False) 
    situation_summary = Column(String(150), nullable=False)  
    emotion_summary = Column(JSON, nullable=False)  
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
    emotion_percentages = relationship("EmotionPercentage", back_populates="report")

class Chatroom(Base):
    __tablename__ = "chatroom"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)  
    update_report_id = Column(Integer, nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(KST))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(KST), onupdate=lambda: datetime.now(KST))
    # 관계 설정
    user = relationship("User", back_populates="chatrooms")
    emotion_chooses = relationship("EmotionChoose", back_populates="chatroom")
    
class Emotion(Base):
    __tablename__ = 'emotion'  # 테이블 이름
    id = Column(Integer, primary_key=True, index=True)  # 기본 키
    emotion_name = Column(String(10), nullable=False)
    explanation = Column(String(100), nullable=False)
    wording=Column(String(150),nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(KST))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(KST),
        onupdate=lambda: datetime.now(KST),
    )
    is_deleted = Column(Boolean, default=False)
    # 외래 키 관계 설정
    emotion_percentages = relationship("EmotionPercentage", back_populates="emotion")
    emotion_chooses = relationship("EmotionChoose", back_populates="emotion")


class EmotionChoose(Base):
    __tablename__ = "emotion_choose"
    id = Column(Integer, primary_key=True)
    chatroom_id = Column(Integer, ForeignKey("chatroom.id"), nullable=False)  # 채팅방 ID
    emotion_id = Column(Integer, ForeignKey("emotion.id"), nullable=False)  # 선택된 감정 ID
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(KST))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(KST), onupdate=lambda: datetime.now(KST))
    # 관계 설정
    chatroom = relationship("Chatroom", back_populates="emotion_chooses")
    emotion = relationship("Emotion", back_populates="emotion_chooses")


class EmotionPercentage(Base):
    __tablename__ = 'emotion_percentage'
    id = Column(Integer, primary_key=True, index=True)  # 기본 키
    report_id = Column(Integer, ForeignKey('report.id'), nullable=False)  # 외래 키
    emotion_id = Column(Integer, ForeignKey('emotion.id'), nullable=False)  # 외래 키
    percentages = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(KST))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(KST),
        onupdate=lambda: datetime.now(KST),
    )
    is_deleted = Column(Boolean, default=False)
    # 외래 키 관계 설정
    report = relationship("Report", back_populates="emotion_percentages")
    emotion = relationship("Emotion", back_populates="emotion_percentages")

