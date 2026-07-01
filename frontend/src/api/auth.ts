import { post, get, put } from "./request";

export interface WeChatLoginRequest {
  code: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

export interface UserResponse {
  id: string;
  openid: string;
  unionid?: string;
  nickname?: string;
  avatar_url?: string;
  gender?: string;
  phone?: string;
  preferences: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserUpdateRequest {
  nickname?: string;
  avatar_url?: string;
  gender?: string;
  phone?: string;
  preferences?: Record<string, any>;
}

export const wechatLogin = (data: WeChatLoginRequest) =>
  post<LoginResponse>("/login/wechat", data);

export const getUserInfo = () => get<UserResponse>("/user/me");

export const updateUserInfo = (data: UserUpdateRequest) =>
  put<UserResponse>("/user/me", data);