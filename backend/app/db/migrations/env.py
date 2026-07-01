"""
Alembic 迁移环境：把异步 DATABASE_URL 转为同步驱动供迁移使用，
并注册所有模型到 Base.metadata，使 autogenerate 能检测变更。
"""
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# 把 backend 目录加入 sys.path，使 app.* 可导入
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from app.core.config import settings  # noqa: E402
from app.db.session import Base  # noqa: E402
# 显式导入所有模型，确保 metadata 完整
from app.models.user import User  # noqa: E402,F401
from app.models.ingredient import Ingredient, IngredientSession  # noqa: E402,F401
from app.models.recipe import Recipe, Recommendation  # noqa: E402,F401
from app.models.favorite import Favorite  # noqa: E402,F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _sync_url() -> str:
    """把异步 DATABASE_URL 转为同步驱动 URL"""
    url = settings.DATABASE_URL
    # asyncpg -> psycopg2
    url = url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    # aiosqlite -> sqlite
    url = url.replace("sqlite+aiosqlite://", "sqlite://")
    return url


def run_migrations_offline() -> None:
    context.configure(
        url=_sync_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=url_sync_is_sqlite(),
    )
    with context.begin_transaction():
        context.run_migrations()


def url_sync_is_sqlite() -> bool:
    return _sync_url().startswith("sqlite")


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = _sync_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=url_sync_is_sqlite(),
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
