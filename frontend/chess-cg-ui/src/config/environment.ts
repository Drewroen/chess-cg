// Centralized environment variable configuration

export const config = {
  backendUrl: process.env.REACT_APP_BACKEND_URL || "http://localhost:8000",
  websocketUrl:
    process.env.REACT_APP_BACKEND_URL + "/ws" || "ws://127.0.0.1:8000/ws",
} as const;

export const { backendUrl, websocketUrl } = config;
