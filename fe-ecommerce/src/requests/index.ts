import  {Authorization} from '@/utils/auth.utils';
import axios from "axios";
export const axiosClient = axios.create({
  baseURL: "http://localhost:8000/api/",
  timeout: 30000,
});

axiosClient.interceptors.request.use(
  (config) => {
    const token = Authorization.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

axiosClient.interceptors.response.use(
 (response) => { 
    return response
 },
 async (error) => { 
    if (error.response?.status === 401) {
      // Chỉ auto-logout khi lỗi 401 là do token hết hạn / không hợp lệ
      const currentPath = window.location.pathname;
      const isAuthPage = currentPath === "/login" || currentPath === "/register";
      const detail = error.response?.data?.detail || error.response?.data?.message;

      let shouldLogout = false;

      if (!isAuthPage && typeof detail === "string") {
        const normalized = detail.toLowerCase();
        const tokenErrorKeywords = [
          "token has experied",
          "token has expired",
          "token was error",
          "token error",
          "invalid token",
          "token không hợp lệ",
          "token het han",
          "token hết hạn",
        ];

        shouldLogout = tokenErrorKeywords.some((keyword) =>
          normalized.includes(keyword),
        );
      }

      if (shouldLogout) {
        Authorization.saveToken("");
        localStorage.removeItem("user");
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
 
)





