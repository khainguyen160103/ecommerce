import  {Authorization} from '@/utils/auth.utils';
import axios from "axios";
export const axiosClient = axios.create({
  baseURL: "http://backend:8000/api/",
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
  if(error.response?.status === 401) { 
    return window.location.href = '/login'
  }
  return Promise.reject(error)
 }
 
)





