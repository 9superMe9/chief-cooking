"""
菜谱图片生成服务：优先返回 AI 生成的真实食物照片（静态文件），不存在时回退到 SVG。
"""
import hashlib
import os
from typing import Optional, Tuple
from xml.sax.saxutils import escape

from app.models.recipe import Recipe

# 静态图片目录（generate_images.py 生成的真实食物照片存放于此）
STATIC_RECIPE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "static", "recipes")


# 菜谱名 -> 专属 emoji（覆盖所有种子菜谱，让图片更贴切）
RECIPE_EMOJI: dict[str, str] = {
    "番茄炒蛋": "🍳", "蛋炒饭": "🍳", "番茄蛋汤": "🍲", "鸡蛋羹": "🥚",
    "西红柿鸡蛋面": "🍜", "青椒炒蛋": "🫑", "红烧肉": "🥩", "清蒸鱼": "🐟",
    "宫保鸡丁": "🍗", "土豆丝": "🥔", "炒青菜": "🥬", "麻婆豆腐": "🧈",
    "糖醋排骨": "🍖", "酸菜鱼": "🐟", "蒜蓉西兰花": "🥦", "回锅肉": "🥩",
    "蒜蓉虾": "🦐", "炒土豆丝": "🥔", "酸辣汤": "🍲", "鱼香肉丝": "🍖",
    "西兰花炒虾仁": "🦐", "肉末茄子": "🍆", "凉拌黄瓜": "🥒", "青椒土豆丝": "🥔",
    "蚝油生菜": "🥬", "清蒸排骨": "🍖", "西红柿炖牛腩": "🥩", "凉拌番茄": "🍅",
    "黄瓜炒鸡蛋": "🥒", "炒虾仁": "🦐", "青椒炒牛肉": "🥩", "青椒肉丝": "🫑",
    "番茄牛腩": "🍅", "芹菜炒牛肉": "🥬", "洋葱炒牛肉": "🧅", "土豆烧牛肉": "🥔",
    "肉末豆腐": "🧈", "番茄鸡蛋面": "🍜", "黄瓜炒肉片": "🥒", "鸡蛋炒饭": "🍚",
    "紫菜蛋花汤": "🍲", "醋溜白菜": "🥬",
}

# 分类 -> (emoji, 渐变起始色, 渐变结束色)
CATEGORY_STYLE: dict[str, Tuple[str, str, str]] = {
    "素菜": ("🥬", "#4A7C59", "#2D5A3D"),
    "蔬菜": ("🥬", "#4A7C59", "#2D5A3D"),
    "肉类": ("🥩", "#B0533A", "#8B3A2A"),
    "海鲜": ("🦐", "#4A90A4", "#2C6A7E"),
    "汤羹": ("🍲", "#C8763A", "#A85A2A"),
    "汤类": ("🍲", "#C8763A", "#A85A2A"),
    "主食": ("🍚", "#D4A537", "#B0852A"),
    "豆制品": ("🧈", "#C8B076", "#A8905A"),
    "凉菜": ("🥒", "#6BA368", "#4A8350"),
    "家常菜": ("🍳", "#C8946A", "#A8744A"),
}

DEFAULT_STYLE: Tuple[str, str, str] = ("🍽️", "#8A8275", "#5A5042")


def _pick_emoji(recipe_name: str, category: str) -> str:
    """优先用菜谱名匹配的 emoji，其次用分类默认 emoji"""
    if recipe_name in RECIPE_EMOJI:
        return RECIPE_EMOJI[recipe_name]
    if category in CATEGORY_STYLE:
        return CATEGORY_STYLE[category][0]
    return DEFAULT_STYLE[0]


def _pick_colors(category: str) -> Tuple[str, str]:
    """按分类取渐变配色"""
    if category in CATEGORY_STYLE:
        _, c1, c2 = CATEGORY_STYLE[category]
        return c1, c2
    return DEFAULT_STYLE[1], DEFAULT_STYLE[2]


def generate_recipe_svg(recipe: Recipe) -> str:
    """
    生成菜谱封面 SVG：渐变背景 + 半透明圆 + 大 emoji + 菜名。
    正方形 400x400，适配前端 aspectFill 裁剪。
    """
    name = recipe.name or "未知菜谱"
    category = recipe.category or ""
    emoji = _pick_emoji(name, category)
    color1, color2 = _pick_colors(category)
    safe_name = escape(name)
    safe_emoji = escape(emoji)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{color1}"/>
      <stop offset="100%" stop-color="{color2}"/>
    </linearGradient>
  </defs>
  <rect width="400" height="400" fill="url(#bg)"/>
  <circle cx="200" cy="165" r="105" fill="rgba(255,255,255,0.14)"/>
  <text x="200" y="195" font-size="115" text-anchor="middle" dominant-baseline="central">{safe_emoji}</text>
  <text x="200" y="340" font-size="38" fill="#ffffff" text-anchor="middle" font-weight="bold" font-family="system-ui,sans-serif" letter-spacing="2">{safe_name}</text>
</svg>'''


def build_recipe_image_url(recipe_id: str, base_url: str) -> str:
    """拼接菜谱图片端点的完整 URL"""
    base = base_url.rstrip("/")
    return f"{base}/api/v1/recipes/{recipe_id}/image"


def _name_slug(name: str) -> str:
    """菜谱名 -> 文件名 slug（与 generate_images.py 的 slugify 一致）"""
    return hashlib.md5(name.encode("utf-8")).hexdigest()[:12]


def get_static_image_path(recipe_name: str) -> Optional[str]:
    """查找菜谱对应的真实食物照片路径，不存在返回 None"""
    slug = _name_slug(recipe_name)
    path = os.path.join(STATIC_RECIPE_DIR, f"{slug}.jpg")
    if os.path.isfile(path) and os.path.getsize(path) > 1000:
        return path
    return None
