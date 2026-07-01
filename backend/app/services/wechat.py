"""微信 OAuth 服务：jscode2session 换 openid；未配置 AppID 时走 mock。"""
import httpx
from typing import Optional, Dict, Any

from app.core.config import settings


class WeChatOAuthService:
    def __init__(self):
        self.app_id = settings.WECHAT_APP_ID
        self.app_secret = settings.WECHAT_APP_SECRET
        self.token_url = "https://api.weixin.qq.com/sns/jscode2session"

    async def get_openid(self, code: str) -> Optional[Dict[str, Any]]:
        if not self.app_id or not self.app_secret or self.app_id.startswith("your-"):
            return {"openid": f"test_openid_{code}", "unionid": None}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.token_url,
                    params={
                        "appid": self.app_id,
                        "secret": self.app_secret,
                        "js_code": code,
                        "grant_type": "authorization_code",
                    },
                )
                data = response.json()
                if "openid" in data:
                    return data
                return None
        except Exception:
            return None