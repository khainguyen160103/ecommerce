import { LOCAL_STOREAGE_TOKEN , LOCAL_STOREAGE_USER , LOCAL_STOREAGE_EXP} from "./constant"
import { AuthService } from "@/requests/auth"
import { UserInfor } from "@/types/user"
export const Authorization = {
  saveToken: (token: string, exp?: string) => {
    localStorage.setItem(LOCAL_STOREAGE_TOKEN, token);
    if (exp) {
      localStorage.setItem(LOCAL_STOREAGE_EXP, exp);
    } else {
      localStorage.setItem(LOCAL_STOREAGE_EXP, "");
    }
  },
  getToken: () => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(LOCAL_STOREAGE_TOKEN);
  },
  saveUserInfor: (userInfor: UserInfor) => {
    localStorage.setItem(LOCAL_STOREAGE_USER, JSON.stringify(userInfor));
  },
  getUserInfor: () => {
    if (typeof window === "undefined") return null;
    const result = localStorage.getItem(LOCAL_STOREAGE_USER);
    if (result) {
      return JSON.parse(result);
    } else {
      return null;
    }
  },
  logout: async () => {
    try {
      await AuthService.logout();
    } catch {
      // EMPTY
    } finally {
      Authorization.saveToken("");
      window.location.replace("/login");
      localStorage.removeItem(LOCAL_STOREAGE_USER);
    }
  },
};

export const TokenService = { 
    getExpiresTime : () => { 
        if (typeof window === "undefined") return null;

        const expiresTime = localStorage.getItem(LOCAL_STOREAGE_EXP)
        
        if(!expiresTime) return null; 

        const expiresNumber = Number(expiresTime)

        if(!isNaN(expiresNumber)) { 
            return new Date(expiresNumber * 1000)
        }
        return new Date(expiresNumber)
    },
    isTokenExpired:  () => {
    if (typeof window === "undefined") return null;
        const expireTime = TokenService.getExpiresTime(); 

        if (!expireTime) return true
        return new Date > expireTime
    }
}
