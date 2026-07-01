"""建表入口：启动时 create_all 自动建表（开发用）；生产用 alembic 迁移。"""
from app.db.session import Base
from app.db.session import engine
from app.models.user import User
from app.models.ingredient import Ingredient, IngredientSession
from app.models.recipe import Recipe, Recommendation
from app.models.favorite import Favorite


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
