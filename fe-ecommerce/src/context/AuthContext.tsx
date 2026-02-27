'use client'
import { useContext, createContext, useState, useCallback } from "react";
import type { ReactNode } from "react";
import { AuthService } from "@/requests/auth";
import { Authorization, TokenService } from "@/utils/auth.utils";
import type { AxiosResponse } from "axios";
import toast from "react-hot-toast";
interface AuthContextType {
    loading: boolean,
    error: null | string
    login: (username: string, password: string) => Promise<AxiosResponse<any, any, {}> | undefined>,
    logout: () => Promise<void>
    register: (username: string, email: string, password: string) => Promise<AxiosResponse<any, any> | undefined>,
    checkAuth : () => boolean,
    googleLogin: (credential: string) => Promise<AxiosResponse<any, any> | undefined>,
    facebookLogin: (accessToken: string) => Promise<AxiosResponse<any, any> | undefined>,
}

export const defaultValue: AuthContextType = {
    loading: false,
    error: null,
    login: async () => {
        throw new Error('AuthProvider not initialized')

    },
    logout: async () => {
        throw new Error('AuthProvider not initialized')

    },
    register: async () => {
        throw new Error('AuthProvider not initialized')

    },
    checkAuth: () => false, 
    googleLogin: async () => {
        throw new Error('AuthProvider not initialized')
    },
    facebookLogin: async () => {
        throw new Error('AuthProvider not initialized')
    },
}
const AuthContext = createContext<AuthContextType>(defaultValue)

const useAuth = () => {
    const context = useContext(AuthContext)
    if (!context) {
        throw new Error("useAuth have to use inside Auth Provider")
    }
    return context
}
interface AuthProviderProps {
    children?: ReactNode
}
const AuthProvider = ({ children }: AuthProviderProps) => {
    const [loading, setLoading] = useState<boolean>(false)
    const [error, setError] = useState<string | null>(null)

    const login = async (email: string, password: string) => {
        setError(null)
        setLoading(true)
        try {
            const res = await AuthService.login({ username: email, password })

            if (res) {
                Authorization.saveToken(res.data?.access_token, String(res.data.expiresIn))
            }
            const userInfor = await AuthService.getMe()
            const { data } = userInfor
            if (userInfor) {
                Authorization.saveUserInfor(data)
            }
            return userInfor;
        } catch (error: any) {
            setError(error)
            console.log(error)
            toast.error("Tài khoản hoặc mật khẩu không chính xác")
        } finally {
            setLoading(false)
        }
    }
    const checkAuth = useCallback(() => { 
        const token = Authorization.getToken() 
        return !!token 
    }, [])

    const logout = async () => {
        await Authorization.logout()
    }

    const register = async (username: string, email: string, password: string) => {
        setError(null)
        setLoading(true)
        try {
            const res = await AuthService.register({ username, email, password })
            return res
        } catch (error: any) {
            setError(error?.response?.data?.detail || "Đăng ký thất bại")
            const errorMsg = error?.response?.data?.detail || "Đăng ký thất bại"
            toast.error(errorMsg)
            throw error
        } finally {
            setLoading(false)
        }
    }

    const _handleOAuthResponse = async (res: AxiosResponse) => {
        if (res?.data?.access_token) {
            Authorization.saveToken(res.data.access_token, String(res.data.expiresIn))
            const userInfor = await AuthService.getMe()
            if (userInfor) {
                Authorization.saveUserInfor(userInfor.data)
            }
            return userInfor
        }
        return res
    }

    const googleLogin = async (credential: string) => {
        setError(null)
        setLoading(true)
        try {
            const res = await AuthService.googleLogin(credential)
            return await _handleOAuthResponse(res)
        } catch (error: any) {
            setError(error?.response?.data?.detail || "Đăng nhập Google thất bại")
            toast.error(error?.response?.data?.detail || "Đăng nhập Google thất bại")
        } finally {
            setLoading(false)
        }
    }

    const facebookLogin = async (accessToken: string) => {
        setError(null)
        setLoading(true)
        try {
            const res = await AuthService.facebookLogin(accessToken)
            return await _handleOAuthResponse(res)
        } catch (error: any) {
            setError(error?.response?.data?.detail || "Đăng nhập Facebook thất bại")
            toast.error(error?.response?.data?.detail || "Đăng nhập Facebook thất bại")
        } finally {
            setLoading(false)
        }
    }

    const value = {
        checkAuth,
        login,
        logout,
        register,
        loading,
        error,
        googleLogin,
        facebookLogin,
    }
    return <AuthContext.Provider value={value}>{children} </AuthContext.Provider>
}

export {
    AuthProvider,
    useAuth
}
