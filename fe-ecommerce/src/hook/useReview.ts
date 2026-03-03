import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ReviewService } from "@/requests/review";
import { CreateReviewInput, UpdateReviewInput } from "@/models/review";
import toast from "react-hot-toast";

export const useReview = (productId?: string) => {
  const queryClient = useQueryClient();

  // Lấy danh sách đánh giá theo sản phẩm
  const reviewsData = useQuery({
    queryKey: ["reviews", productId],
    queryFn: () => ReviewService.getByProduct(productId!, 1, 100),
    enabled: !!productId,
  });

  // Lấy đánh giá của tôi cho sản phẩm
  const myReviewData = useQuery({
    queryKey: ["myReview", productId],
    queryFn: () => ReviewService.getMyReview(productId!),
    enabled: !!productId,
  });

  // Kiểm tra điều kiện đánh giá (có đơn hàng giao thành công không)
  const eligibilityData = useQuery({
    queryKey: ["reviewEligibility", productId],
    queryFn: () => ReviewService.checkEligibility(productId!),
    enabled: !!productId,
  });

  // Tạo đánh giá
  const createReview = useMutation({
    mutationFn: ({
      productId,
      data,
    }: {
      productId: string;
      data: CreateReviewInput;
    }) => ReviewService.create(productId, data),
    onSuccess: (_, { productId }) => {
      toast.success("Đánh giá thành công!");
      queryClient.invalidateQueries({ queryKey: ["reviews", productId] });
      queryClient.invalidateQueries({ queryKey: ["myReview", productId] });
      queryClient.invalidateQueries({
        queryKey: ["reviewEligibility", productId],
      });
    },
    onError: (error: any) => {
      const message =
        error?.response?.data?.detail || "Có lỗi xảy ra khi đánh giá";
      toast.error(message);
    },
  });

  // Cập nhật đánh giá
  const updateReview = useMutation({
    mutationFn: ({
      reviewId,
      data,
    }: {
      reviewId: string;
      data: UpdateReviewInput;
    }) => ReviewService.update(reviewId, data),
    onSuccess: () => {
      toast.success("Cập nhật đánh giá thành công!");
      queryClient.invalidateQueries({ queryKey: ["reviews", productId] });
      queryClient.invalidateQueries({ queryKey: ["myReview", productId] });
      queryClient.invalidateQueries({
        queryKey: ["reviewEligibility", productId],
      });
    },
    onError: () => {
      toast.error("Có lỗi xảy ra khi cập nhật đánh giá");
    },
  });

  // Xóa đánh giá
  const deleteReview = useMutation({
    mutationFn: (reviewId: string) => ReviewService.delete(reviewId),
    onSuccess: () => {
      toast.success("Xóa đánh giá thành công!");
      queryClient.invalidateQueries({ queryKey: ["reviews", productId] });
      queryClient.invalidateQueries({ queryKey: ["myReview", productId] });
      queryClient.invalidateQueries({
        queryKey: ["reviewEligibility", productId],
      });
    },
    onError: () => {
      toast.error("Có lỗi xảy ra khi xóa đánh giá");
    },
  });

  return {
    reviewsData,
    myReviewData,
    eligibilityData,
    createReview,
    updateReview,
    deleteReview,
  };
};;
