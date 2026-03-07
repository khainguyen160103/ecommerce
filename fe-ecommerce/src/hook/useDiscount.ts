import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { DiscountService } from "@/requests/discount";
import toast from "react-hot-toast";
import type { CreateDiscountInput, UpdateDiscountInput } from "@/models/discount";

interface UseDiscountOptions {
  /**
   * Bật/tắt việc gọi API getAll mã giảm giá (chỉ ADMIN mới dùng).
   *  - true: dùng cho trang admin (mặc định)
   *  - false: dùng cho trang user (checkout) để tránh 401 không cần thiết
   */
  enableGetAll?: boolean;
}

export const useDiscount = (options?: UseDiscountOptions) => {
  const queryClient = useQueryClient();
  const enableGetAll = options?.enableGetAll ?? true;

  const discountsData = useQuery({
    // Dùng key riêng cho trang admin để không ảnh hưởng tới trang user (checkout)
    queryKey: ["discounts-admin"],
    queryFn: () => DiscountService.getAll(),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
    enabled: enableGetAll,
  });

  const createMutation = useMutation({
    mutationFn: (data: CreateDiscountInput) => DiscountService.create(data),
    onSuccess: () => {
      toast.success("Tạo mã giảm giá thành công");
      queryClient.invalidateQueries({ queryKey: ["discounts"] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Lỗi tạo mã giảm giá");
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateDiscountInput }) =>
      DiscountService.update(id, data),
    onSuccess: () => {
      toast.success("Cập nhật mã giảm giá thành công");
      queryClient.invalidateQueries({ queryKey: ["discounts"] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Lỗi cập nhật mã giảm giá");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => DiscountService.delete(id),
    onSuccess: () => {
      toast.success("Xóa mã giảm giá thành công");
      queryClient.invalidateQueries({ queryKey: ["discounts"] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Lỗi xóa mã giảm giá");
    },
  });

  const useApplyDiscount = () => {
    return useMutation({
      mutationFn: ({ code, subtotal }: { code: string; subtotal: number }) =>
        DiscountService.apply(code, subtotal),
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || "Mã giảm giá không hợp lệ");
      },
    });
  };

  return {
    discountsData,
    createMutation,
    updateMutation,
    deleteMutation,
    useApplyDiscount,
  };
};
