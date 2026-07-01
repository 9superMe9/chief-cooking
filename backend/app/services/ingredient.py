"""食材服务：食材字典维护、食材会话（一次录入流程）的增删查。"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ingredient import Ingredient, IngredientSession
from app.models.user import User
from app.schemas.ingredient import IngredientCreate, IngredientSessionCreate, IngredientSessionUpdate


class IngredientService:
    @staticmethod
    async def get_all_ingredients(db: AsyncSession) -> List[Ingredient]:
        result = await db.execute(select(Ingredient))
        return result.scalars().all()

    @staticmethod
    async def get_ingredient_by_name(db: AsyncSession, name: str) -> Optional[Ingredient]:
        result = await db.execute(select(Ingredient).where(Ingredient.name == name))
        return result.scalars().first()

    @staticmethod
    async def create_ingredient(db: AsyncSession, ingredient_data: IngredientCreate) -> Ingredient:
        ingredient = Ingredient(**ingredient_data.model_dump())
        db.add(ingredient)
        await db.commit()
        await db.refresh(ingredient)
        return ingredient

    @staticmethod
    async def ensure_ingredient_exists(db: AsyncSession, name: str) -> Ingredient:
        ingredient = await IngredientService.get_ingredient_by_name(db, name)
        if not ingredient:
            ingredient = await IngredientService.create_ingredient(db, IngredientCreate(name=name))
        return ingredient


class IngredientSessionService:
    @staticmethod
    async def create_session(db: AsyncSession, user_id: Optional[str], session_data: IngredientSessionCreate) -> IngredientSession:
        session = IngredientSession(
            user_id=user_id,
            ingredients=session_data.ingredients,
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def get_user_active_session(db: AsyncSession, user_id: Optional[str]) -> Optional[IngredientSession]:
        query = select(IngredientSession).where(IngredientSession.status == "active")
        if user_id:
            query = query.where(IngredientSession.user_id == user_id)
        else:
            query = query.where(IngredientSession.user_id.is_(None))
        query = query.order_by(IngredientSession.created_at.desc())
        result = await db.execute(query)
        return result.scalars().first()

    @staticmethod
    async def get_session_by_id(db: AsyncSession, session_id: str) -> Optional[IngredientSession]:
        result = await db.execute(select(IngredientSession).where(IngredientSession.id == session_id))
        return result.scalars().first()

    @staticmethod
    async def update_session(db: AsyncSession, session: IngredientSession, update_data: IngredientSessionUpdate) -> IngredientSession:
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(session, key, value)
        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def close_session(db: AsyncSession, session: IngredientSession) -> IngredientSession:
        session.status = "closed"
        await db.commit()
        await db.refresh(session)
        return session