"""用户模型：openid/unionid/昵称/头像/偏好偏好字段。"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, JSON, String, Boolean, Text

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    openid = Column(String(128), unique=True, index=True, nullable=False)
    unionid = Column(String(128), unique=True, index=True, nullable=True)
    nickname = Column(String(128), nullable=True)
    avatar_url = Column(String(512), nullable=True)
    gender = Column(String(10), nullable=True)
    phone = Column(String(20), nullable=True)
    preferences = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)