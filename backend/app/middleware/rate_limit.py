"""
接口限流中间件：基于内存滑动窗口，按路由前缀 + 客户端 IP 维度限速。
单实例部署够用；多实例需替换为 Redis 实现。
被限流时返回 429 Too Many Requests。
"""
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import settings


# 路由前缀 -> 每分钟允许请求数
_ROUTE_LIMITS = {
    "/api/v1/login": settings.RATE_LIMIT_LOGIN_PER_MIN,
    "/api/v1/upload": settings.RATE_LIMIT_UPLOAD_PER_MIN,
    "/api/v1/ingredients/recognize": settings.RATE_LIMIT_AI_PER_MIN,
    "/api/v1/recipes/recommend": settings.RATE_LIMIT_RECOMMEND_PER_MIN,
}


def _client_ip(request: Request) -> str:
    """优先取反向代理转发的真实 IP，否则取连接 IP"""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _match_limit(path: str) -> Tuple[str, int]:
    """返回命中的 (路由前缀, 限流值)；未命中返回 ("", 0)"""
    for prefix, limit in _ROUTE_LIMITS.items():
        if path.startswith(prefix):
            return prefix, limit
    return "", 0


class RateLimitMiddleware(BaseHTTPMiddleware):
    """滑动窗口限流：每 (prefix, ip) 维护一个 60 秒内的请求时间队列"""

    def __init__(self, app):
        super().__init__(app)
        # key: (prefix, ip) -> deque[float]
        self._buckets: Dict[Tuple[str, str], Deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        prefix, limit = _match_limit(path)
        if not limit:
            return await call_next(request)

        ip = _client_ip(request)
        key = (prefix, ip)
        now = time.monotonic()
        window = 60.0
        bucket = self._buckets[key]

        # 清理过期记录
        while bucket and now - bucket[0] > window:
            bucket.popleft()

        if len(bucket) >= limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "请求过于频繁，请稍后再试"},
            )

        bucket.append(now)
        return await call_next(request)
