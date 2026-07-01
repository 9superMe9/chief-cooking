"""
敏感词过滤工具：内置基础敏感词表，提供命中检测与替换。
用于过滤用户输入食材名、AI 输出文本，避免小程序内容安全审核被拒。
生产可替换为更完整的词库或接入微信内容安全接口 msg_sec_check。
"""
from typing import List

# 基础敏感词示例（政治/色情/暴力/广告类常见词根，生产建议扩展或外接词库）
SENSITIVE_WORDS: List[str] = [
    "Fuck", "fuck", "SHIT", "shit",
    "操你", "草你", "傻逼", "sb", "SB",
    "婊", "妓", "嫖", "黄赌毒",
    "法轮", "六四", "台独", "港独", "藏独",
    "反共", "反华", "推翻",
    "色情", "裸体", "裸照", "av女优",
    "杀人", "自杀方法", "制毒", "贩毒",
    "代开发票", "办证", "出售身份证",
]

# 替换为等长星号
_REPLACEMENT = "*"


def contains_sensitive(text: str) -> bool:
    """是否包含敏感词"""
    if not text:
        return False
    return any(word in text for word in SENSITIVE_WORDS)


def find_sensitive(text: str) -> List[str]:
    """返回命中的敏感词列表"""
    if not text:
        return []
    return [word for word in SENSITIVE_WORDS if word in text]


def mask_sensitive(text: str) -> str:
    """把敏感词替换为等长星号"""
    if not text:
        return text
    masked = text
    for word in SENSITIVE_WORDS:
        if word in masked:
            masked = masked.replace(word, _REPLACEMENT * len(word))
    return masked


def is_text_safe(text: str) -> bool:
    """文本是否安全（不包含敏感词）"""
    return not contains_sensitive(text)
