import { axiosClient } from "."
import { ENDPOINT } from "./endpoint"

export const CategoryService = { 
    getAll: async () => await axiosClient.get(ENDPOINT.CATEGORY.GET_ALL),
    getById: async (id: string) => await axiosClient.get(ENDPOINT.CATEGORY.GET_BY_ID(id)),
    create: async (data: any) => await axiosClient.post(ENDPOINT.CATEGORY.CREATE, data),
    update: async (id: string, data: any) => await axiosClient.put(ENDPOINT.CATEGORY.UPDATE(id), data),
    delete: async (id: string) => await axiosClient.delete(ENDPOINT.CATEGORY.DELETE(id))
}