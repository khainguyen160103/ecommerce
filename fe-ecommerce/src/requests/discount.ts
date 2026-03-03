import { axiosClient } from ".";
import { ENDPOINT } from "./endpoint";
import type { Discount, CreateDiscountInput, UpdateDiscountInput, ApplyDiscountResult } from "@/models/discount";

export const DiscountService = {
  // Admin
  getAll: async () => 
    await axiosClient.get(ENDPOINT.DISCOUNT.GET_ALL),

  getById: async (id: string) =>
    await axiosClient.get(ENDPOINT.DISCOUNT.GET_BY_ID(id)),

  create: async (data: CreateDiscountInput) =>
    await axiosClient.post(ENDPOINT.DISCOUNT.CREATE, data),

  update: async (id: string, data: UpdateDiscountInput) =>
    await axiosClient.put(ENDPOINT.DISCOUNT.UPDATE(id), data),

  delete: async (id: string) =>
    await axiosClient.delete(ENDPOINT.DISCOUNT.DELETE(id)),

  // User
  apply: async (code: string, subtotal: number) =>
    await axiosClient.post(ENDPOINT.DISCOUNT.APPLY, { code, subtotal }),
};
