import { axiosClient } from "."
import { ENDPOINT } from "./endpoint"
export const UserService = { 
    getAll: async () => await axiosClient.get(ENDPOINT.USER.GETALL),
    getById: async (id: string) => await axiosClient.get(ENDPOINT.USER.GET_BY_ID(id)),
    create: async (data: any) => await axiosClient.post(ENDPOINT.USER.CREATE, data),
    update: async (id: string, data: any) => await axiosClient.put(ENDPOINT.USER.UPDATE(id), data),
    delete: async (id: string) => await axiosClient.delete(ENDPOINT.USER.DELETE(id))
}