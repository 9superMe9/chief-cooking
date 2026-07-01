import { get, post, del } from "./request";

export interface RecipeResponse {
  id: string;
  name: string;
  description?: string;
  ingredients: string[];
  matched_ingredients: string[];
  missing_ingredients: string[];
  steps: string[];
  cooking_time?: string;
  servings?: string;
  taste?: string;
  difficulty?: string;
  category?: string;
  image_url?: string;
  ai_reason?: string;
  risk_tags: string[];
  alternative_suggestions: any;
  recommendation_reason: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface RecommendationRequest {
  session_id?: string;
  ingredients?: string[];
  preferences?: Record<string, any>;
  mode?: "strict" | "flexible" | "any";
}

export interface RecommendationResponse {
  recipes: RecipeResponse[];
  total: number;
  downgraded?: boolean;
  soup_warning?: string;
}

export const getRecipes = () => get<RecipeResponse[]>("/recipes");

export const getRecipeById = (id: string) => get<RecipeResponse>(`/recipes/${id}`);

export const getRecipe = (id: string) => get<RecipeResponse>(`/recipes/${id}`);

export const recommendRecipes = (data: RecommendationRequest) =>
  post<RecommendationResponse>("/recipes/recommend", data);

export const addFavorite = (recipeId: string) => 
  post(`/favorites/${recipeId}`);

export const removeFavorite = (recipeId: string) => 
  del(`/favorites/${recipeId}`);

export const getFavoriteStatus = (recipeId: string) => 
  get(`/favorites/${recipeId}/status`);

export const getFavorites = () => get<RecipeResponse[]>("/favorites");

// ---------- 历史记录 ----------

export interface HistoryItem {
  recommendation_id: string;
  created_at: string;
  recipes: RecipeResponse[];
}

export interface HistoryResponse {
  history: HistoryItem[];
  total: number;
}

export const getRecommendationHistory = (limit = 20) =>
  get<HistoryResponse>(`/recommendations/history?limit=${limit}`);