import { defineStore } from "pinia";
import { ref } from "vue";
import {
  createIngredientSession,
  getActiveSession,
  updateIngredientSession,
} from "../api/ingredients";
import { recommendRecipes, type RecipeResponse } from "../api/recipes";

export interface Ingredient {
  id: string;
  name: string;
  quantity?: string;
  category?: string;
  confidence?: number;
}

export interface Preferences {
  people?: number;
  cookingTime: string;
  taste: string;
  peopleTags: string[];
  restrictions: string[];
  difficulty: string;
}

export const useRecipeStore = defineStore("recipe", () => {
  const ingredients = ref<Ingredient[]>([]);
  const preferences = ref<Preferences>({
    people: 2,
    cookingTime: "",
    taste: "",
    peopleTags: [],
    restrictions: [],
    difficulty: "",
  });
  const sessionId = ref<string>("");
  const recommendedRecipes = ref<RecipeResponse[]>([]);
  const currentRecipe = ref<RecipeResponse | null>(null);
  // 推荐模式：strict(在家用现有食材) / flexible(允许补1-2样) / any(在超市选购)
  const recommendMode = ref<"strict" | "flexible" | "any">("strict");

  function setIngredients(items: Ingredient[]) {
    ingredients.value = items;
  }

  function addIngredient(item: Ingredient) {
    if (!ingredients.value.find((i) => i.name === item.name)) {
      ingredients.value.push(item);
    }
  }

  function removeIngredient(id: string) {
    ingredients.value = ingredients.value.filter((i) => i.id !== id);
  }

  function updateIngredient(id: string, updates: Partial<Ingredient>) {
    const index = ingredients.value.findIndex((i) => i.id === id);
    if (index !== -1) {
      ingredients.value[index] = { ...ingredients.value[index], ...updates };
    }
  }

  function setPreferences(prefs: Preferences) {
    preferences.value = prefs;
  }

  function setSessionId(id: string) {
    sessionId.value = id;
  }

  function setRecommendMode(mode: "strict" | "flexible" | "any") {
    recommendMode.value = mode;
  }

  function setRecommendedRecipes(recipes: RecipeResponse[]) {
    recommendedRecipes.value = recipes;
  }

  function setCurrentRecipe(recipe: RecipeResponse | null) {
    currentRecipe.value = recipe;
  }

  async function saveSession() {
    const ingredientNames = ingredients.value.map((i) => i.name);
    if (sessionId.value) {
      await updateIngredientSession(sessionId.value, { ingredients: ingredientNames });
    } else {
      const response = await createIngredientSession({ ingredients: ingredientNames });
      sessionId.value = response.id;
    }
  }

  async function loadSession() {
    try {
      const response = await getActiveSession();
      sessionId.value = response.id;
      ingredients.value = response.ingredients.map((name, index) => ({
        id: `ing-${index}`,
        name,
      }));
    } catch {
      ingredients.value = [];
      sessionId.value = "";
    }
  }

  async function getRecommendations() {
    const ingredientNames = ingredients.value.map((i) => i.name);
    const response = await recommendRecipes({
      session_id: sessionId.value,
      ingredients: ingredientNames,
      preferences: preferences.value,
      mode: recommendMode.value,
    });
    recommendedRecipes.value = response.recipes;
    return response.recipes;
  }

  function clear() {
    ingredients.value = [];
    preferences.value = {
      people: 2,
      cookingTime: 20,
      taste: "家常",
      peopleTags: [],
      restrictions: [],
    };
    sessionId.value = "";
    recommendedRecipes.value = [];
    currentRecipe.value = null;
  }

  return {
    ingredients,
    preferences,
    sessionId,
    recommendedRecipes,
    currentRecipe,
    recommendMode,
    setIngredients,
    addIngredient,
    removeIngredient,
    updateIngredient,
    setPreferences,
    setSessionId,
    setRecommendMode,
    setRecommendedRecipes,
    setCurrentRecipe,
    saveSession,
    loadSession,
    getRecommendations,
    clear,
  };
});