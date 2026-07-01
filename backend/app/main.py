"""
FastAPI 应用入口：注册路由、CORS、静态资源、启动建表。
生产环境(APP_ENV=production)自动关闭 /docs 与 /redoc，CORS 限定白名单。
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.ingredients import router as ingredients_router
from app.api.v1.recipes import router as recipes_router
from app.api.v1.upload import router as upload_router
from app.api.v1.favorites import router as favorites_router
from app.core.config import settings
from app.core.logging import logger
from app.db.base import create_tables
from app.middleware.rate_limit import RateLimitMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="饭点小厨 AI 私厨助手后端 API",
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 接口限流中间件：按路由组分别限速
app.add_middleware(RateLimitMiddleware)

app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(ingredients_router, prefix="/api/v1")
app.include_router(recipes_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")
app.include_router(favorites_router, prefix="/api/v1")

app.mount("/uploads", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "uploads")), name="uploads")

# H5 前端静态文件（同源部署时；目录存在才挂载，不影响 /api/v1 和 /uploads 路由）
from pathlib import Path
_h5_dir = Path(__file__).resolve().parent.parent / "static"
if _h5_dir.exists():
    app.mount("/", StaticFiles(directory=str(_h5_dir), html=True), name="h5")
    logger.info(f"H5 静态文件已挂载: {_h5_dir}")


@app.on_event("startup")
async def startup_event():
    await create_tables()
    logger.info(f"{settings.APP_NAME} 启动成功 (env={settings.APP_ENV})")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"{settings.APP_NAME} 关闭")
