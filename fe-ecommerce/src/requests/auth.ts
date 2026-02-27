import { axiosClient } from './index';
import { ENDPOINT } from './endpoint';

export const AuthService = {
    login: async (data: { username: string, password: string }) => await axiosClient.post(ENDPOINT.AUTH.LOGIN, data, {
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        }
    }),
    register: async (data: { username: string, email: string, password: string }) => await axiosClient.post(ENDPOINT.AUTH.REGISTER, data),
    getMe: async () => await axiosClient.get(ENDPOINT.AUTH.ME),
    logout: async () => await axiosClient.post(ENDPOINT.AUTH.LOGOUT),
    googleLogin: async (credential: string) => await axiosClient.post(ENDPOINT.AUTH.GOOGLE, { credential }),
    facebookLogin: async (accessToken: string) => await axiosClient.post(ENDPOINT.AUTH.FACEBOOK, { access_token: accessToken }),
    changePassword: async (data: { old_password: string, new_password: string }) => await axiosClient.post(ENDPOINT.AUTH.CHANGE_PASSWORD, data),
}
