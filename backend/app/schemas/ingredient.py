"""食材相关 Pydantic 模型：食材字典与会话的请求/响应结构。"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class IngredientCreate(BaseModel):
    name: str
    category: Optional[str] = None
    unit: Optional[str] = None


class IngredientResponse(BaseModel):
    id: str
    name: str
    category: Optional[str] = None
    unit: Optional[str] = None
    is_common: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IngredientSessionCreate(BaseModel):
    ingredients: List[str] = Field(..., description="食材名称列表")


class IngredientSessionUpdate(BaseModel):
    ingredients: Optional[List[str]] = None
    status: Optional[str] = None


class IngredientSessionResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    ingredients: List[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True