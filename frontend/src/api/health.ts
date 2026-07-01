import { get } from "./request";

export interface HealthResponse {
  status: string;
}

export const healthCheck = () => get<HealthResponse>("/health");