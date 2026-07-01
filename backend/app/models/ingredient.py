"""食材与食材会话模型：食材字典 + 一次录入会话。"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Boolean, JSON, ForeignKey

from app.db.session import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(128), nullable=False)
    category = Column(String(64), nullable=True)
    unit = Column(String(32), nullable=True)
    is_common = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class IngredientSession(Base):
    __tablename__ = "ingredient_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    ingredients = Column(JSON, default=list)
    status = Column(String(32), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)