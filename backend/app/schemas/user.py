"""用户相关 Pydantic 模型：登录/创建/更新/响应结构。"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    openid: str
    unionid: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    gender: Optional[str] = None


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    preferences: Optional[dict] = None


class UserResponse(BaseModel):
    id: UUID
    openid: str
    unionid: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    preferences: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WeChatLoginRequest(BaseModel):
    code: str = Field(..., description="微信登录临时凭证code")


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    user: UserResponse