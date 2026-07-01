"""健康检查路由：GET /health 返回服务状态；GET /ai/usage 查看 AI token 用量。"""
from fastapi import APIRouter

from app.core.config import settings
from app.utils.token_usage import get_summary

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok"}


@router.get("/ai/usage")
async def ai_usage():
    """查看 AI token 累计用量与免费额度余量"""
    summary = get_summary()
    quota = settings.AI_FREE_QUOTA_TOKENS
    total = summary.get("total_tokens", 0)
    return {
        "total_tokens": total,
        "prompt_tokens": summary.get("prompt_tokens", 0),
        "completion_tokens": summary.get("completion_tokens", 0),
        "call_count": summary.get("call_count", 0),
        "free_quota_tokens": quota,
        "remaining_tokens": max(quota - total, 0) if quota > 0 else None,
        "used_ratio": round(total / quota, 4) if quota > 0 else None,
        "models": {
            "vision": settings.AI_VISION_MODEL,
            "text": settings.AI_TEXT_MODEL,
        },
    }
