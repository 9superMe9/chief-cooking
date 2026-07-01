"""收藏服务：菜谱收藏的增删查业务逻辑。"""
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.favorite import Favorite
from app.models.user import User
from app.models.recipe import Recipe


class FavoriteService:
    @staticmethod
    async def get_user_favorites(db: AsyncSession, user: User) -> List[Recipe]:
        result = await db.execute(
            select(Favorite).where(Favorite.user_id == str(user.id))
        )
        favorites = result.scalars().all()
        
        recipe_ids = [f.recipe_id for f in favorites]
        if not recipe_ids:
            return []
        
        result = await db.execute(
            select(Recipe).where(Recipe.id.in_(recipe_ids))
        )
        return result.scalars().all()

    @staticmethod
    async def add_favorite(db: AsyncSession, user: User, recipe_id: str) -> Favorite:
        existing = await db.execute(
            select(Favorite).where(
                Favorite.user_id == str(user.id),
                Favorite.recipe_id == recipe_id
            )
        )
        if existing.scalars().first():
            return existing.scalars().first()
        
        favorite = Favorite(
            user_id=str(user.id),
            recipe_id=recipe_id,
        )
        db.add(favorite)
        await db.commit()
        await db.refresh(favorite)
        return favorite

    @staticmethod
    async def remove_favorite(db: AsyncSession, user: User, recipe_id: str) -> bool:
        result = await db.execute(
            delete(Favorite).where(
                Favorite.user_id == str(user.id),
                Favorite.recipe_id == recipe_id
            )
        )
        await db.commit()
        return result.rowcount > 0

    @staticmethod
    async def is_favorited(db: AsyncSession, user: User, recipe_id: str) -> bool:
        result = await db.execute(
            select(Favorite).where(
                Favorite.user_id == str(user.id),
                Favorite.recipe_id == recipe_id
            )
        )
        return result.scalars().first() is not None