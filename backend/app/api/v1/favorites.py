"""收藏路由：菜谱收藏的增删查与状态查询。"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.recipe import RecipeResponse
from app.services.favorite import FavoriteService
from app.services.image import build_recipe_image_url

router = APIRouter()


@router.get("/favorites", response_model=List[RecipeResponse])
async def get_favorites(
    request: Request,
    user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user:
        return []
    recipes = await FavoriteService.get_user_favorites(db, user)
    base_url = str(request.base_url)
    for r in recipes:
        if not r.image_url:
            r.image_url = build_recipe_image_url(r.id, base_url)
    return recipes


@router.post("/favorites/{recipe_id}")
async def add_favorite(
    recipe_id: str,
    user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    await FavoriteService.add_favorite(db, user, recipe_id)
    return {"message": "收藏成功"}


@router.delete("/favorites/{recipe_id}")
async def remove_favorite(
    recipe_id: str,
    user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    success = await FavoriteService.remove_favorite(db, user, recipe_id)
    if not success:
        raise HTTPException(status_code=404, detail="收藏不存在")
    return {"message": "取消收藏成功"}


@router.get("/favorites/{recipe_id}/status")
async def get_favorite_status(
    recipe_id: str,
    user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user:
        return {"is_favorited": False}
    is_favorited = await FavoriteService.is_favorited(db, user, recipe_id)
    return {"is_favorited": is_favorited}