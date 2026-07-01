/**
 * 统一请求封装：BASE_URL 从环境变量读取（VITE_API_BASE_URL），
 * 自动携带 JWT token，统一处理 401/网络异常/错误提示。
 * 小程序提审时 VITE_API_BASE_URL 必须为已备案的 HTTPS 域名。
 */
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

interface RequestOptions {
  url: string;
  method?: "GET" | "POST" | "PUT" | "DELETE";
  data?: any;
  header?: any;
  timeout?: number;
}

export function request<T = any>(options: RequestOptions): Promise<T> {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync("token");
    const headers: any = {
      "Content-Type": "application/json",
      ...options.header,
    };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    uni.request({
      url: `${BASE_URL}${options.url}`,
      method: options.method || "GET",
      data: options.data,
      header: headers,
      timeout: options.timeout || 10000,
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data);
        } else if (res.statusCode === 401) {
          const existingToken = uni.getStorageSync("token");
          if (existingToken) {
            uni.removeStorageSync("token");
            uni.removeStorageSync("user");
            uni.showToast({ title: "登录已过期", icon: "none" });
            setTimeout(() => {
              uni.navigateTo({ url: "/pages/index/index" });
            }, 1500);
          }
          reject(res.data);
        } else {
          uni.showToast({
            title: res.data?.message || res.data?.detail || "请求失败",
            icon: "none",
          });
          reject(res.data);
        }
      },
      fail: (err) => {
        uni.showToast({ title: "网络请求失败", icon: "none" });
        reject(err);
      },
    });
  });
}

export const get = <T = any>(url: string, data?: any) =>
  request<T>({ url, method: "GET", data });

export const post = <T = any>(url: string, data?: any) =>
  request<T>({ url, method: "POST", data });

export const put = <T = any>(url: string, data?: any) =>
  request<T>({ url, method: "PUT", data });

export const del = <T = any>(url: string, data?: any) =>
  request<T>({ url, method: "DELETE", data });

export { BASE_URL };
