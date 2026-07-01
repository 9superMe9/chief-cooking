import { get, post, put, request, BASE_URL } from "./request";

export interface IngredientResponse {
  id: string;
  name: string;
  category?: string;
  unit?: string;
  is_common: boolean;
  created_at: string;
  updated_at: string;
}

export interface IngredientSessionCreate {
  ingredients: string[];
}

export interface IngredientSessionResponse {
  id: string;
  user_id: string;
  ingredients: string[];
  status: string;
  created_at: string;
  updated_at: string;
}

export interface IngredientSessionUpdate {
  ingredients?: string[];
  status?: string;
}

export const getIngredients = () => get<IngredientResponse[]>("/ingredients");

export const createIngredientSession = (data: IngredientSessionCreate) =>
  post<IngredientSessionResponse>("/ingredient-session", data);

export const getActiveSession = () =>
  get<IngredientSessionResponse>("/ingredient-session/active");

export const updateIngredientSession = (
  sessionId: string,
  data: IngredientSessionUpdate
) => put<IngredientSessionResponse>(`/ingredient-session/${sessionId}`, data);

// ---------- 拍照识别相关 ----------

export interface UploadImageResponse {
  file_id: string;
  image_url: string;
  filename: string;
  size: number;
}

export interface RecognizedIngredient {
  id: string;
  name: string;
  category: string;
  confidence: number;
  status: string;
}

export interface RecognizeResponse {
  file_id: string;
  image_url: string;
  ingredients: RecognizedIngredient[];
  ai_available: boolean;
  message: string;
}

/** 上传图片到后端，返回 file_id 和 image_url */
export function uploadImage(filePath: string): Promise<UploadImageResponse> {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync("token");
    uni.uploadFile({
      url: `${BASE_URL}/upload/image`,
      filePath,
      name: "file",
      header: token ? { Authorization: `Bearer ${token}` } : {},
      success: (res) => {
        if (res.statusCode === 200) {
          try {
            resolve(JSON.parse(res.data));
          } catch (e) {
            reject(e);
          }
        } else {
          reject(res);
        }
      },
      fail: (err) => reject(err),
    });
  });
}

/** 调用后端 AI 识别接口，返回识别到的食材列表 */
export function recognizeIngredients(fileId: string, imageUrl: string) {
  const query = `file_id=${encodeURIComponent(fileId)}&image_url=${encodeURIComponent(imageUrl)}`;
  // AI 多模态识别较慢，单独给 60 秒超时（默认 10 秒不够）
  return request<RecognizeResponse>({
    url: `/ingredients/recognize?${query}`,
    method: "POST",
    timeout: 60000,
  });
}