"""食材路由：食材字典查询、食材会话创建/查询/更新（含敏感词校验）。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.ingredient import (
    IngredientResponse,
    IngredientSessionCreate,
    IngredientSessionResponse,
    IngredientSessionUpdate,
)
from app.services.ingredient import IngredientService, IngredientSessionService
from app.utils.sensitive_words import is_text_safe

router = APIRouter()


@router.get("/ingredients", response_model=List[IngredientResponse])
async def get_ingredients(db: AsyncSession = Depends(get_db)):
    return await IngredientService.get_all_ingredients(db)


@router.post("/ingredient-session", response_model=IngredientSessionResponse)
async def create_ingredient_session(
    session_data: IngredientSessionCreate,
    user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 食材名做敏感词校验，命中则拒绝
    for ingredient_name in session_data.ingredients:
        if not is_text_safe(ingredient_name):
            raise HTTPException(status_code=400, detail=f"食材名包含不合规内容：{ingredient_name}")
        await IngredientService.ensure_ingredient_exists(db, ingredient_name)
    user_id = str(user.id) if user else None
    return await IngredientSessionService.create_session(db, user_id, session_data)


@router.get("/ingredient-session/active", response_model=IngredientSessionResponse)
async def get_active_session(
    user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = str(user.id) if user else None
    session = await IngredientSessionService.get_user_active_session(db, user_id)
    if not session:
        raise HTTPException(status_code=404, detail="没有找到活跃的食材会话")
    return session


@router.put("/ingredient-session/{session_id}", response_model=IngredientSessionResponse)
async def update_ingredient_session(
    session_id: str,
    update_data: IngredientSessionUpdate,
    user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await IngredientSessionService.get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="食材会话不存在")
    user_id = str(user.id) if user else None
    if session.user_id and session.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权修改此会话")
    if update_data.ingredients:
        for ingredient_name in update_data.ingredients:
            if not is_text_safe(ingredient_name):
                raise HTTPException(status_code=400, detail=f"食材名包含不合规内容：{ingredient_name}")
            await IngredientService.ensure_ingredient_exists(db, ingredient_name)
    return await IngredientSessionService.update_session(db, session, update_data)