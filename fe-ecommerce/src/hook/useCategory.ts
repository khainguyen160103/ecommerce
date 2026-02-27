import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CategoryService } from "@/requests/category";
import toast from "react-hot-toast";

export const useCategory = (categoryId?: string) => {
  const queryClient = useQueryClient();

  const categoriesData = useQuery({
    queryKey: ["categories"],
    queryFn: () => CategoryService.getAll(),
    staleTime: 5 * 60 * 1000, // ✅ Cache 5 phút
    gcTime: 10 * 60 * 1000,
  });

  const categoryIdData = useQuery({
    queryKey: ["category", categoryId],
    queryFn: () => CategoryService.getById(categoryId ? categoryId : ""),
    enabled: !!categoryId,
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => CategoryService.create(data),
    onSuccess: () => {
      toast.success("Tạo danh mục thành công");
      queryClient.invalidateQueries({ queryKey: ["categories"] });
    },
    onError: () => {
      toast.error("Lỗi tạo danh mục");
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      CategoryService.update(id, data),
    onSuccess: () => {
      toast.success("Cập nhật danh mục thành công");
      queryClient.invalidateQueries({ queryKey: ["categories"] });
    },
    onError: () => {
      toast.error("Lỗi cập nhật danh mục");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => CategoryService.delete(id),
    onSuccess: () => {
      toast.success("Xóa danh mục thành công");
      queryClient.invalidateQueries({ queryKey: ["categories"] });
    },
    onError: () => {
      toast.error("Lỗi xóa danh mục");
    },
  });

  return {
    categoriesData,
    categoryIdData,
    createMutation,
    updateMutation,
    deleteMutation,
  };
};
