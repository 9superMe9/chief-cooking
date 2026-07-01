"""菜谱路由：列表/详情/推荐/历史；含菜谱封面图端点（真实食物照片优先，回退 SVG）。"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.ingredient import IngredientSession
from app.models.recipe import Recipe, Recommendation
from app.schemas.recipe import RecipeResponse, RecommendationRequest, RecommendationResponse, RecipeRecommendationResponse
from app.services.recipe import RecipeService, AI_RECIPE_MARKER, _core_ingredients, _normalize_ingredients
from app.services.ingredient import IngredientSessionService
from app.services.ai import AIService
from app.services.image import generate_recipe_svg, build_recipe_image_url, get_static_image_path

router = APIRouter()


def _fill_image_url(recipe, base_url: str):
    """菜谱 image_url 为空时，自动填充为后端动态图片端点 URL"""
    if recipe and not recipe.image_url:
        recipe.image_url = build_recipe_image_url(recipe.id, base_url)
    return recipe


@router.get("/recipes", response_model=List[RecipeResponse])
async def get_recipes(request: Request, db: AsyncSession = Depends(get_db)):
    await RecipeService.ensure_mock_recipes(db)
    recipes = await RecipeService.get_all_recipes(db)
    # 浏览列表不展示 AI 动态生成的临时菜谱
    recipes = [r for r in recipes if r.ai_reason != AI_RECIPE_MARKER]
    base_url = str(request.base_url)
    for r in recipes:
        _fill_image_url(r, base_url)
    return recipes


@router.get("/recipes/{recipe_id}/image")
async def get_recipe_image(recipe_id: str, db: AsyncSession = Depends(get_db)):
    """返回菜谱封面图：优先真实食物照片，回退到 SVG"""
    recipe = await RecipeService.get_recipe_by_id(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="菜谱不存在")
    # 优先返回 AI 生成的真实食物照片
    static_path = get_static_image_path(recipe.name)
    if static_path:
        return FileResponse(static_path, media_type="image/jpeg", headers={"Cache-Control": "public, max-age=604800"})
    # 回退到 SVG 占位图
    svg = generate_recipe_svg(recipe)
    return Response(content=svg, media_type="image/svg+xml", headers={"Cache-Control": "public, max-age=86400"})


@router.get("/recipes/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(recipe_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    recipe = await RecipeService.get_recipe_by_id(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="菜谱不存在")
    _fill_image_url(recipe, str(request.base_url))
    return recipe


@router.post("/recipes/recommend", response_model=RecommendationResponse)
async def recommend_recipes(
    request: RecommendationRequest,
    http_request: Request,
    user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ingredients = request.ingredients or []
    
    if request.session_id:
        session = await IngredientSessionService.get_session_by_id(db, request.session_id)
        if session:
            user_id = str(user.id) if user else None
            if session.user_id is None or session.user_id == user_id:
                ingredients = session.ingredients
    
    # 推荐数量：优先用用户选择的"几菜几汤"，默认5
    recommend_count = 5
    if request.preferences and request.preferences.get("recommendCount"):
        try:
            recommend_count = int(request.preferences["recommendCount"])
        except (ValueError, TypeError):
            pass

    recipes, downgraded, soup_warning = await RecipeService.recommend_recipes(
        db, ingredients, request.preferences, limit=recommend_count, mode=request.mode
    )
    
    recipe_ids = [recipe.id for recipe in recipes]
    user_id = str(user.id) if user else None
    await RecipeService.save_recommendation(db, user_id, request.session_id, recipe_ids)
    
    # 批量 AI 润色推荐理由（失败降级模板）
    recipes_info = [
        {
            "name": recipe.name,
            "matched": list(set(recipe.ingredients).intersection(set(ingredients))),
        }
        for recipe in recipes
    ]
    ai_reasons = await AIService.polish_reasons_batch(
        recipes_info, ingredients, request.preferences
    )

    enhanced_recipes = []
    base_url = str(http_request.base_url)
    for recipe in recipes:
        _fill_image_url(recipe, base_url)
        # 归一化后计算 matched/missing，保证与推荐逻辑一致
        norm_recipe_ings = set(_normalize_ingredients(recipe.ingredients or []))
        norm_user_ings = set(_normalize_ingredients(ingredients or []))

        # matched 用完整食材：用户选了葱花也显示为"已有"
        matched_ingredients = list(norm_recipe_ings.intersection(norm_user_ings))
        # missing 只算核心食材：葱花/温水等辅料不算缺失
        core_set = set(_core_ingredients(_normalize_ingredients(recipe.ingredients or [])))
        missing_ingredients = list(core_set - norm_user_ings)
        
        enhanced_steps = AIService.enhance_recipe_steps(
            recipe.name, recipe.steps, request.preferences
        )
        
        recommendation_reason = ai_reasons.get(recipe.name) or AIService.polish_recommendation_reason(
            recipe.name, matched_ingredients, request.preferences
        )
        
        alternative_suggestions = AIService.generate_alternative_suggestions(
            recipe.name, missing_ingredients
        )
        
        risk_tags = RecipeService.get_risk_tags(recipe, request.preferences)
        
        enhanced_recipes.append(RecipeRecommendationResponse(
            id=recipe.id,
            name=recipe.name,
            description=recipe.description,
            ingredients=recipe.ingredients,
            matched_ingredients=matched_ingredients,
            missing_ingredients=missing_ingredients,
            steps=enhanced_steps,
            cooking_time=recipe.cooking_time,
            servings=recipe.servings,
            taste=recipe.taste,
            difficulty=recipe.difficulty,
            category=recipe.category,
            risk_tags=risk_tags,
            alternative_suggestions=alternative_suggestions,
            recommendation_reason=recommendation_reason,
            image_url=recipe.image_url,
        ))

    # 固定菜谱库匹配不足 3 道时，调用 AI 动态生成补充菜谱
    if len(enhanced_recipes) < 3 and ingredients:
        ai_recipes_data = await AIService.generate_recipes_with_ai(ingredients, count=3)
        existing_names = {r.name for r in enhanced_recipes}
        norm_user_ings = set(_normalize_ingredients(ingredients or []))
        for recipe_data in ai_recipes_data:
            if recipe_data["name"] in existing_names:
                continue
            ai_recipe = Recipe(
                id=str(uuid.uuid4()),
                ai_reason=AI_RECIPE_MARKER,
                image_url="",
                **recipe_data,
            )
            db.add(ai_recipe)
            await db.flush()

            _fill_image_url(ai_recipe, base_url)

            norm_ai_ings = set(_normalize_ingredients(ai_recipe.ingredients or []))
            matched_ai = list(norm_ai_ings.intersection(norm_user_ings))
            core_ai = set(_core_ingredients(list(norm_ai_ings)))
            missing_ai = list(core_ai - norm_user_ings)

            enhanced_steps = AIService.enhance_recipe_steps(
                ai_recipe.name, ai_recipe.steps, request.preferences
            )
            risk_tags = RecipeService.get_risk_tags(ai_recipe, request.preferences)

            enhanced_recipes.append(RecipeRecommendationResponse(
                id=ai_recipe.id,
                name=ai_recipe.name,
                description=ai_recipe.description,
                ingredients=ai_recipe.ingredients,
                matched_ingredients=matched_ai,
                missing_ingredients=missing_ai,
                steps=enhanced_steps,
                cooking_time=ai_recipe.cooking_time,
                servings=ai_recipe.servings,
                taste=ai_recipe.taste,
                difficulty=ai_recipe.difficulty,
                category=ai_recipe.category,
                risk_tags=risk_tags,
                alternative_suggestions={},
                recommendation_reason=f"AI 根据你现有的{', '.join(matched_ai[:3] or ingredients[:3])}创意推荐",
                image_url=ai_recipe.image_url,
            ))
            existing_names.add(ai_recipe.name)

        if ai_recipes_data:
            await db.commit()

    return RecommendationResponse(
        recipes=enhanced_recipes,
        total=len(enhanced_recipes),
        downgraded=downgraded,
        soup_warning=soup_warning,
    )


@router.get("/recommendations/history")
async def get_recommendation_history(
    http_request: Request,
    limit: int = 20,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的推荐历史记录，按时间倒序，含菜谱详情"""
    user_id = str(user.id)
    result = await db.execute(
        select(Recommendation)
        .where(Recommendation.user_id == user_id)
        .order_by(Recommendation.created_at.desc())
        .limit(limit)
    )
    recommendations = result.scalars().all()

    base_url = str(http_request.base_url)
    history = []
    for rec in recommendations:
        recipes = []
        for rid in rec.recipe_ids or []:
            recipe = await RecipeService.get_recipe_by_id(db, rid)
            if recipe:
                _fill_image_url(recipe, base_url)
                recipes.append(recipe)
        history.append({
            "recommendation_id": rec.id,
            "created_at": rec.created_at.isoformat() if rec.created_at else None,
            "recipes": recipes,
        })

    return {"history": history, "total": len(history)}