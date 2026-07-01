"""AI 服务：多模态食材识别、推荐理由批量润色、动态菜谱生成；AI 不可用时降级到本地模板。"""
import hashlib
import json
import re
import time
from typing import List, Optional

import httpx

from app.core.config import settings
from app.core.logging import logger
from app.utils.sensitive_words import mask_sensitive, is_text_safe
from app.utils.token_usage import record_usage

# AI 菜谱生成缓存：食材组合 hash -> (生成时间戳, 菜谱列表)
_AI_RECIPE_CACHE: dict = {}
_AI_CACHE_TTL = 600  # 10 分钟内相同食材组合不重复调用 AI


def _is_ai_configured() -> bool:
    """AI 是否已配置可用（API Key 非占位符）"""
    return bool(settings.AI_API_KEY) and not settings.AI_API_KEY.startswith("your-")


def _strip_json_text(text: str) -> str:
    """从大模型输出中提取 JSON 文本（去除 markdown 代码块和多余说明）"""
    if not text:
        return ""
    # 去除 ```json ... ``` 或 ``` ... ``` 包裹
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()
    # 尝试直接找第一个 { 或 [ 到最后一个 } 或 ]
    start = text.find("{")
    if start == -1:
        start = text.find("[")
    if start != -1:
        end = text.rfind("}")
        if end == -1:
            end = text.rfind("]")
        if end != -1:
            return text[start:end + 1]
    return text.strip()


def _safe_json_loads(text: str):
    """容错 JSON 解析，失败返回 None"""
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        return None


async def _call_chat_api(messages: list, model: str, temperature: float = 0.3) -> Optional[str]:
    """调用 OpenAI 兼容的 chat completions 接口，失败返回 None。记录 token 用量。"""
    if not _is_ai_configured():
        return None
    url = f"{settings.AI_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.AI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "enable_thinking": False,
    }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            # 记录 token 用量并检查免费额度
            usage = data.get("usage")
            if usage:
                summary = record_usage(model, usage)
                logger.info(f"AI 调用({model}) 用量: {usage.get('total_tokens')} tokens, 累计 {summary['total_tokens']}")
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.warning(f"AI 调用失败({model}): {e}")
        return None


class AIService:
    @staticmethod
    async def recognize_ingredients(image_data_url: str) -> List[dict]:
        """
        多模态食材识别：输入图片(base64 data url 或公网 url)，返回食材列表。
        失败或未配置 AI 时返回空列表，由调用方降级到手动输入。
        """
        prompt = (
            "请识别图片中清晰可见的食材。要求：\n"
            "1. 只识别清晰可见的食材，不要猜测被遮挡或包装内的食材\n"
            "2. 不判断食材新鲜度\n"
            "3. 食材名用中文，如番茄、鸡蛋、豆腐\n"
            "4. 只返回 JSON，格式："
            '{"ingredients":[{"name":"食材名","category":"蔬菜/肉类/蛋品/豆制品/主食/海鲜/其他","confidence":0.9}]}'
            "\n5. confidence 取值 0-1，表示识别置信度\n"
            "6. 如果图片中没有食材，返回 {\"ingredients\":[]}"
        )
        messages = [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_data_url}},
                {"type": "text", "text": prompt},
            ],
        }]
        content = await _call_chat_api(messages, settings.AI_VISION_MODEL, 0.1)
        if not content:
            return []
        data = _safe_json_loads(_strip_json_text(content))
        if not isinstance(data, dict):
            return []
        ingredients = data.get("ingredients", [])
        result = []
        for item in ingredients:
            if isinstance(item, dict) and item.get("name"):
                name = str(item["name"]).strip()
                # AI 输出做内容安全过滤：敏感词遮罩，命中则丢弃该食材
                if not is_text_safe(name):
                    name = mask_sensitive(name)
                if name:
                    result.append({
                        "name": name,
                        "category": item.get("category", "其他"),
                        "confidence": float(item.get("confidence", 0.8)),
                    })
        return result

    @staticmethod
    async def polish_reasons_batch(recipes_info: List[dict], user_ingredients: List[str], preferences: Optional[dict] = None) -> dict:
        """
        批量润色推荐理由，返回 {菜谱名: 理由}。
        recipes_info: [{"name": "番茄炒蛋", "matched": ["番茄","鸡蛋"]}, ...]
        失败时返回空 dict，由调用方降级到模板。
        """
        if not recipes_info:
            return {}
        taste = (preferences or {}).get("taste", "")
        people_tags = (preferences or {}).get("peopleTags", [])
        lines = []
        for i, r in enumerate(recipes_info):
            matched = ",".join(r.get("matched", [])[:3])
            lines.append(f"{i + 1}. {r['name']}（可用食材：{matched}）")
        prompt = (
            "请为以下每道菜写一句推荐理由，要求自然口语化、不超过30字，结合用户现有食材。\n"
            f"用户口味偏好：{taste or '不限'}；用餐人群：{','.join(people_tags) or '不限'}\n"
            "菜谱列表：\n" + "\n".join(lines) + "\n"
            '只返回 JSON，格式：{"1":"理由1","2":"理由2"}，key 用上面的序号数字字符串，不要加"理由"二字。'
        )
        messages = [{"role": "user", "content": prompt}]
        content = await _call_chat_api(messages, settings.AI_TEXT_MODEL, 0.7)
        if not content:
            return {}
        data = _safe_json_loads(_strip_json_text(content))
        if not isinstance(data, dict):
            return {}
        result = {}
        for i, r in enumerate(recipes_info):
            reason = data.get(str(i + 1)) or data.get(r["name"])
            if reason:
                # AI 推荐理由做内容安全过滤
                result[r["name"]] = mask_sensitive(str(reason).strip())
        return result

    @staticmethod
    async def generate_recipes_with_ai(ingredients: List[str], count: int = 3) -> List[dict]:
        """
        根据用户食材调用 AI 动态生成菜谱（当固定菜谱库匹配不足时补充）。
        10 分钟内相同食材组合直接返回缓存，避免重复消耗 token。
        返回菜谱 dict 列表（未入库），失败时返回空列表。
        """
        if not ingredients or not _is_ai_configured():
            return []

        # 缓存 key：排序去重后的食材组合 hash
        cache_key = hashlib.md5(
            ",".join(sorted(set(ingredients))).encode("utf-8")
        ).hexdigest()

        # 命中缓存直接返回
        cached = _AI_RECIPE_CACHE.get(cache_key)
        if cached:
            cached_time, cached_recipes = cached
            if time.time() - cached_time < _AI_CACHE_TTL:
                logger.info(f"AI 菜谱生成命中缓存（{len(cached_recipes)} 道菜谱）")
                return cached_recipes

        prompt = (
            f"你是一位经验丰富的中餐厨师。用户现有以下食材：{', '.join(ingredients)}\n"
            f"请根据这些食材创作 {count} 道菜谱。要求：\n"
            "1. 优先使用用户现有食材，可添加少量常见调味料（盐、生抽、料酒、食用油等）\n"
            "2. 菜谱要实用、可操作，适合家庭烹饪\n"
            "3. 每道菜的步骤要具体清晰，4-6 步\n"
            "4. 只返回 JSON，格式：\n"
            '{"recipes":[{"name":"菜名","description":"简短描述","ingredients":["食材1","食材2"],'
            '"steps":["步骤1","步骤2"],"cooking_time":"15分钟","servings":"2人份",'
            '"taste":"咸鲜","difficulty":"简单","category":"家常菜","risk_tags":[]}]}'
        )
        messages = [{"role": "user", "content": prompt}]
        content = await _call_chat_api(messages, settings.AI_TEXT_MODEL, 0.8)
        if not content:
            return []

        data = _safe_json_loads(_strip_json_text(content))
        if not isinstance(data, dict):
            return []

        recipes = data.get("recipes", [])
        result = []
        for r in recipes:
            if not isinstance(r, dict) or not r.get("name"):
                continue
            recipe = {
                "name": mask_sensitive(str(r["name"]).strip()),
                "description": str(r.get("description", "")).strip(),
                "ingredients": r.get("ingredients", []) if isinstance(r.get("ingredients"), list) else [],
                "steps": r.get("steps", []) if isinstance(r.get("steps"), list) else [],
                "cooking_time": str(r.get("cooking_time", "15分钟")).strip(),
                "servings": str(r.get("servings", "2人份")).strip(),
                "taste": str(r.get("taste", "咸鲜")).strip(),
                "difficulty": str(r.get("difficulty", "简单")).strip(),
                "category": str(r.get("category", "家常菜")).strip(),
                "risk_tags": r.get("risk_tags", []) if isinstance(r.get("risk_tags"), list) else [],
            }
            if recipe["name"]:
                result.append(recipe)

        # 写入缓存
        if result:
            _AI_RECIPE_CACHE[cache_key] = (time.time(), result)
            logger.info(f"AI 动态生成 {len(result)} 道菜谱，已缓存（key={cache_key[:8]}）")

        return result

    # ---------- 以下为本地模板降级方法（AI 不可用时使用） ----------

    @staticmethod
    def polish_recommendation_reason(recipe_name: str, ingredients: List[str], preferences: Optional[dict] = None) -> str:
        """本地模板推荐理由（降级用）"""
        reason_templates = [
            f"用你现有的{', '.join(ingredients[:3])}做{recipe_name}再合适不过了，简单又美味！",
            f"{recipe_name}非常适合用{', '.join(ingredients[:2])}来做，是一道经典的家常菜。",
            f"考虑到你的食材，{recipe_name}是个很棒的选择，做法简单，用时也不长。",
            f"{recipe_name}是用{', '.join(ingredients[:2])}做的经典菜式，味道鲜美，营养均衡。",
            f"推荐你做{recipe_name}，正好可以用上你现有的{', '.join(ingredients[:3])}。",
        ]
        if preferences:
            taste = preferences.get("taste")
            cooking_time = preferences.get("cookingTime")
            if taste:
                reason_templates.append(f"按照你喜欢的{taste}口味，{recipe_name}是个完美的选择！")
            if cooking_time:
                reason_templates.append(f"{recipe_name}只需{cooking_time}就能做好，非常适合你！")
        index = hash(recipe_name) % len(reason_templates)
        return reason_templates[index]

    @staticmethod
    def enhance_recipe_steps(recipe_name: str, steps: List[str], preferences: Optional[dict] = None) -> List[str]:
        """本地模板步骤增强（降级用）"""
        enhanced_steps = []
        for i, step in enumerate(steps, 1):
            tips = []
            if preferences:
                people_tags = preferences.get("peopleTags", [])
                if "老人" in people_tags or "小孩" in people_tags:
                    tips.append("（食材煮软一些更适合）")
                if "健身" in people_tags:
                    tips.append("（少油更健康）")
            enhanced_steps.append(f"第{i}步：{step}{''.join(tips)}")
        return enhanced_steps

    @staticmethod
    def generate_alternative_suggestions(recipe_name: str, missing_ingredients: List[str]) -> dict:
        """本地替代食材建议（降级用）"""
        alternatives = {
            "鸡蛋": ["鸭蛋", "鹌鹑蛋"],
            "猪肉": ["牛肉", "鸡肉"],
            "番茄": ["西红柿", "圣女果"],
            "米饭": ["小米饭", "杂粮饭"],
            "青菜": ["菠菜", "生菜", "油麦菜"],
            "豆腐": ["嫩豆腐", "老豆腐", "豆干"],
            "黄瓜": ["小黄瓜", "西葫芦"],
            "土豆": ["红薯", "山药"],
            "青椒": ["彩椒", "尖椒"],
            "鱼": ["鱼片", "虾"],
            "虾仁": ["鲜贝", "鱿鱼"],
            "西兰花": ["菜花", "芥蓝"],
        }
        suggestions = {}
        for ingredient in missing_ingredients:
            if ingredient in alternatives:
                suggestions[ingredient] = alternatives[ingredient]
        return suggestions
