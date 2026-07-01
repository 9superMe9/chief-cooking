"""认证路由：微信登录（code 换 openid 签发 JWT）、获取/更新当前用户信息。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.user import LoginResponse, UserResponse, WeChatLoginRequest, UserUpdate, UserCreate
from app.services.user import UserService
from app.services.wechat import WeChatOAuthService

router = APIRouter()


@router.post("/login/wechat", response_model=LoginResponse)
async def wechat_login(request: WeChatLoginRequest, db: AsyncSession = Depends(get_db)):
    wechat_service = WeChatOAuthService()
    wechat_data = await wechat_service.get_openid(request.code)

    if not wechat_data:
        raise HTTPException(status_code=400, detail="微信登录失败")

    openid = wechat_data.get("openid")
    unionid = wechat_data.get("unionid")

    user = await UserService.get_user_by_openid(db, openid)

    if not user:
        user = await UserService.create_user(
            db,
            user_data=UserCreate(
                openid=openid,
                unionid=unionid,
            ),
        )

    access_token = UserService.generate_token(user)

    return LoginResponse(
        access_token=access_token,
        token_type="Bearer",
        user=user,
    )


@router.get("/user/me", response_model=UserResponse)
async def get_current_user(user: User = Depends(get_current_user)):
    return user


@router.put("/user/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await UserService.update_user(db, user, update_data)