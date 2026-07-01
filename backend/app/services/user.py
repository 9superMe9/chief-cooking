"""用户服务：按 openid 查/建用户、签发 token、更新用户信息与偏好。"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import create_access_token


class UserService:
    @staticmethod
    async def get_user_by_openid(db: AsyncSession, openid: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.openid == openid))
        return result.scalars().first()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        user = User(**user_data.model_dump())
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def update_user(db: AsyncSession, user: User, update_data: UserUpdate) -> User:
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(user, key, value)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    def generate_token(user: User) -> str:
        return create_access_token(data={"sub": str(user.id)})