import { axiosClient } from ".";
import { ENDPOINT } from "./endpoint";

export const ProductService = {
  getAll: async (page: number, limit: number) => {
    try {
      const res = await axiosClient.get(ENDPOINT.PRODUCT.GETALL, {
        params: {
          page,
          limit,
        },
    });
    return res.data
    } catch (error) {
        throw error
    }
  },

  search: async (keyword: string, skip: number = 0, limit: number = 20) => {
    try {
      const res = await axiosClient.get(ENDPOINT.PRODUCT.SEARCH, {
        params: { keyword, skip, limit },
      });
      return res.data;
    } catch (error) {
      throw error;
    }
  },

  getById: async (id: string) =>
    await axiosClient.get(ENDPOINT.PRODUCT.GET_BY_ID(id)),
  create: async (data: FormData) =>
    await axiosClient.post(ENDPOINT.PRODUCT.CREATE || "products", data, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  update: async (id: string, data: any) =>
    await axiosClient.put(ENDPOINT.PRODUCT.UPDATE(id), data),
  delete: async (id: string) =>
    await axiosClient.delete(ENDPOINT.PRODUCT.DELETE(id)),

  // Product Details
  getDetails: async (id: string) =>
    await axiosClient.get(ENDPOINT.PRODUCT.GET_PRODUCT_DETAIL(id)),
  addDetail: async (id: string, data: any) =>
    await axiosClient.post(ENDPOINT.PRODUCT.ADD_PRODUCT_DETAIL(id), data),
  updateDetail: async (productId: string, detailId: string, data: any) =>
    await axiosClient.put(`products/${productId}/details/${detailId}`, data),
  deleteDetail: async (productId: string, detailId: string) =>
    await axiosClient.delete(`products/${productId}/details/${detailId}`),
};
