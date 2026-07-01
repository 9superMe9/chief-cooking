"""菜谱相关 Pydantic 模型：菜谱响应、推荐请求/响应结构。"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class RecipeResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    ingredients: List[str]
    steps: List[str]
    cooking_time: Optional[str] = None
    servings: Optional[str] = None
    taste: Optional[str] = None
    difficulty: Optional[str] = None
    category: Optional[str] = None
    risk_tags: List[str] = []
    image_url: Optional[str] = None
    ai_reason: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecipeRecommendationResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    ingredients: List[str]
    matched_ingredients: List[str]
    missing_ingredients: List[str]
    steps: List[str]
    cooking_time: Optional[str] = None
    servings: Optional[str] = None
    taste: Optional[str] = None
    difficulty: Optional[str] = None
    category: Optional[str] = None
    risk_tags: List[str] = []
    alternative_suggestions: dict = {}
    recommendation_reason: str = ""
    image_url: Optional[str] = None


class RecommendationRequest(BaseModel):
    session_id: Optional[str] = None
    ingredients: Optional[List[str]] = None
    preferences: Optional[dict] = None
    mode: str = "strict"  # strict(严格) / flexible(允许补1-2样) / any(任意)


class RecommendationResponse(BaseModel):
    recipes: List[RecipeRecommendationResponse]
    total: int
    downgraded: bool = False  # 是否触发保底降级（strict 无结果时自动放宽）
    soup_warning: str = ""  # 汤类不足提示（空字符串表示无提示）