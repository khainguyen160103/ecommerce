import { axiosClient } from ".";
import { ENDPOINT } from "./endpoint";
import { CreateReviewInput, UpdateReviewInput } from "@/models/review";

export const ReviewService = {
  getByProduct: async (
    productId: string,
    page: number = 1,
    limit: number = 20,
  ) => {
    const res = await axiosClient.get(
      ENDPOINT.REVIEW.GET_BY_PRODUCT(productId),
      {
        params: { page, limit },
      },
    );
    return res.data;
  },

  getMyReview: async (productId: string) => {
    const res = await axiosClient.get(ENDPOINT.REVIEW.GET_MY_REVIEW(productId));
    return res.data;
  },

  checkEligibility: async (productId: string) => {
    const res = await axiosClient.get(
      ENDPOINT.REVIEW.CHECK_ELIGIBILITY(productId),
    );
    return res.data;
  },

  create: async (productId: string, data: CreateReviewInput) => {
    const res = await axiosClient.post(ENDPOINT.REVIEW.CREATE(productId), data);
    return res.data;
  },

  update: async (reviewId: string, data: UpdateReviewInput) => {
    const res = await axiosClient.put(ENDPOINT.REVIEW.UPDATE(reviewId), data);
    return res.data;
  },

  delete: async (reviewId: string) => {
    const res = await axiosClient.delete(ENDPOINT.REVIEW.DELETE(reviewId));
    return res.data;
  },

  adminDelete: async (reviewId: string) => {
    const res = await axiosClient.delete(
      ENDPOINT.REVIEW.ADMIN_DELETE(reviewId),
    );
    return res.data;
  },
};
