"""
应用配置中心：统一从环境变量/.env 读取所有配置项。
生产部署前必须修改 JWT_SECRET_KEY、CORS_ORIGINS、WECHAT_APP_ID/SECRET、COS_* 等。
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_origins(v) -> List[str]:
    """把逗号分隔的字符串解析为来源列表"""
    if isinstance(v, list):
        return v
    if not v:
        return []
    return [item.strip() for item in v.split(",") if item.strip()]


class Settings(BaseSettings):
    APP_NAME: str = "饭点小厨"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    DATABASE_URL: str = "sqlite+aiosqlite:///./chief_cooking.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET_KEY: str = "your-secret-key-here"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    WECHAT_APP_ID: str = ""
    WECHAT_APP_SECRET: str = ""

    AI_API_KEY: str = ""
    AI_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    AI_VISION_MODEL: str = "qwen3.7-plus"
    AI_TEXT_MODEL: str = "qwen3.7-plus"
    # 百炼免费额度（tokens）；用尽后按定价计费。0 表示不告警。
    # qwen3.7-plus 新用户通常有 100万 tokens 免费额度，按自己账号实际填
    AI_FREE_QUOTA_TOKENS: int = 1000000
    # 用量达到额度的多少比例时告警（0-1）
    AI_COST_WARN_RATIO: float = 0.8

    COS_SECRET_ID: str = ""
    COS_SECRET_KEY: str = ""
    COS_REGION: str = "ap-guangzhou"
    COS_BUCKET: str = ""

    # CORS 允许来源；逗号分隔。生产应填小程序后台配置的域名 + H5 域名
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # 后端对外公网根地址，用于拼接图片公网 URL（如 https://api.example.com）
    PUBLIC_BASE_URL: str = ""

    # 限流：每分钟每个 IP 最多请求数（按路由组分别计数）
    RATE_LIMIT_LOGIN_PER_MIN: int = 10
    RATE_LIMIT_UPLOAD_PER_MIN: int = 20
    RATE_LIMIT_AI_PER_MIN: int = 10
    RATE_LIMIT_RECOMMEND_PER_MIN: int = 20

    @property
    def cors_origins(self) -> List[str]:
        return _parse_origins(self.CORS_ORIGINS)

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
