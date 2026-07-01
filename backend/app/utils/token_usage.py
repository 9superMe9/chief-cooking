"""
AI Token 用量追踪：累计每次大模型调用的 token 消耗到本地文件，
接近免费额度阈值时日志告警，避免超额花钱。
用量持久化到 logs/token_usage.json，重启不丢失。
"""
import json
import os
import threading
from datetime import datetime
from typing import Optional

from app.core.config import settings
from app.core.logging import logger

USAGE_FILE = os.path.join("logs", "token_usage.json")
_lock = threading.Lock()


def _ensure_file() -> None:
    os.makedirs("logs", exist_ok=True)
    if not os.path.exists(USAGE_FILE):
        _write({"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0,
                "call_count": 0, "calls": []})


def _read() -> dict:
    try:
        with open(USAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0,
                "call_count": 0, "calls": []}


def _write(data: dict) -> None:
    try:
        with open(USAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"写入 token 用量文件失败: {e}")


def record_usage(model: str, usage: Optional[dict]) -> dict:
    """
    记录一次调用的 token 用量并返回累计统计。
    usage 形如 {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
    """
    if not usage:
        return get_summary()

    prompt_t = int(usage.get("prompt_tokens", 0))
    completion_t = int(usage.get("completion_tokens", 0))
    total_t = int(usage.get("total_tokens", prompt_t + completion_t))

    with _lock:
        _ensure_file()
        data = _read()
        data["total_tokens"] = data.get("total_tokens", 0) + total_t
        data["prompt_tokens"] = data.get("prompt_tokens", 0) + prompt_t
        data["completion_tokens"] = data.get("completion_tokens", 0) + completion_t
        data["call_count"] = data.get("call_count", 0) + 1
        # 只保留最近 200 条调用明细，避免文件无限增长
        calls = data.get("calls", [])
        calls.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model": model,
            "prompt": prompt_t,
            "completion": completion_t,
            "total": total_t,
        })
        data["calls"] = calls[-200:]
        _write(data)

        _maybe_warn(data["total_tokens"])
        return {
            "total_tokens": data["total_tokens"],
            "call_count": data["call_count"],
        }


def _maybe_warn(total_tokens: int) -> None:
    """达到免费额度阈值时告警（默认 80% 与 100% 各告警一次）"""
    quota = settings.AI_FREE_QUOTA_TOKENS
    if quota <= 0:
        return
    ratio = total_tokens / quota
    if ratio >= 1.0:
        logger.error(
            f"⚠️ AI 免费额度已用尽！累计 {total_tokens} tokens（额度 {quota}），"
            f"后续调用将按百炼定价计费。请到阿里云百炼控制台查看账单。"
        )
    elif ratio >= settings.AI_COST_WARN_RATIO:
        logger.warning(
            f"⚠️ AI 免费额度即将用尽：累计 {total_tokens}/{quota} tokens "
            f"（{ratio:.0%}），请关注用量或充值。"
        )


def get_summary() -> dict:
    """读取当前累计用量"""
    with _lock:
        _ensure_file()
        return _read()
