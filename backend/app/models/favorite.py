"""收藏模型：用户-菜谱多对多关系。"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Boolean

from app.db.session import Base


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False)
    recipe_id = Column(String(36), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)