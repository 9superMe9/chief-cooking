"""菜谱与推荐记录模型：菜谱种子数据、推荐结果存档。"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Boolean, JSON, Text

from app.db.session import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    ingredients = Column(JSON, default=list)
    steps = Column(JSON, default=list)
    cooking_time = Column(String(32), nullable=True)
    servings = Column(String(32), nullable=True)
    taste = Column(String(64), nullable=True)
    difficulty = Column(String(32), nullable=True)
    category = Column(String(64), nullable=True)
    risk_tags = Column(JSON, default=list)
    image_url = Column(String(512), nullable=True)
    ai_reason = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True)
    session_id = Column(String(36), nullable=True)
    recipe_ids = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)