import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ProductService } from "@/requests/product";
import toast from 'react-hot-toast';
import { useState } from "react";

export const useProduct = (productId?: string) => { 
    const queryClient = useQueryClient();
    const [page, setPage] = useState<number>(0); 
    const [limit, setLimit] = useState<number>(20);
    
    const productsData = useQuery({ 
        queryKey: ['products', page, limit],
        queryFn: () => ProductService.getAll(page,limit),
        staleTime: 60 * 60 * 1000
    });

    const productIdData = useQuery({ 
        queryKey: ['product', productId], 
        queryFn: () => ProductService.getById(productId ? productId : ''),
        enabled: !!productId, 
        staleTime: 60 * 60 * 1000
    });

    const productDetailsData = useQuery({
        queryKey: ['productDetails', productId],
        queryFn: () => ProductService.getDetails(productId ? productId : ''),
        enabled: !!productId
    });

    const createMutation = useMutation({ 
        mutationFn: (data: FormData) => ProductService.create(data),
        onSuccess: () => {
            toast.success('Tạo sản phẩm thành công');
            queryClient.invalidateQueries({ queryKey: ['products'] });
        },
        onError: () => {
            toast.error('Lỗi tạo sản phẩm');
        }
    });

    const updateMutation = useMutation({ 
        mutationFn: ({ id, data }: { id: string; data: any }) => 
            ProductService.update(id, data),
        onSuccess: () => {
            toast.success('Cập nhật sản phẩm thành công');
            queryClient.invalidateQueries({ queryKey: ['products'] });
        },
        onError: () => {
            toast.error('Lỗi cập nhật sản phẩm');
        }
    });

    const deleteMutation = useMutation({ 
        mutationFn: (id: string) => ProductService.delete(id),
        onSuccess: () => {
            toast.success('Xóa sản phẩm thành công');
            queryClient.invalidateQueries({ queryKey: ['products'] });
        },
        onError: () => {
            toast.error('Lỗi xóa sản phẩm');
        }
    });

    const addDetailMutation = useMutation({
        mutationFn: ({ productId, data }: { productId: string; data: any }) =>
            ProductService.addDetail(productId, data),
        onSuccess: (_, { productId }) => {
            toast.success('Thêm chi tiết sản phẩm thành công');
            queryClient.invalidateQueries({
              queryKey: ["productDetails", productId]
            });
        },
        onError: () => {
            toast.error('Lỗi thêm chi tiết sản phẩm');
        }
    });

    const updateDetailMutation = useMutation({
        mutationFn: ({ productId, detailId, data }: { productId: string; detailId: string; data: any }) =>
            ProductService.updateDetail(productId, detailId, data),
        onSuccess: (_, { productId }) => {
            toast.success('Cập nhật chi tiết sản phẩm thành công');
            queryClient.invalidateQueries({ queryKey: ['productDetails', productId] });
        },
        onError: () => {
            toast.error('Lỗi cập nhật chi tiết sản phẩm');
        }
    });

    const deleteDetailMutation = useMutation({
        mutationFn: ({ productId, detailId }: { productId: string; detailId: string }) => {
          return  ProductService.deleteDetail(productId, detailId)
        },
        onSuccess: (_, { productId }) => {
            toast.success('Xóa chi tiết sản phẩm thành công');
            queryClient.invalidateQueries({ queryKey: ['productDetails', productId] });
        },
        onError: () => {
            toast.error('Lỗi xóa chi tiết sản phẩm');
        }
    });
    
    return { 
        queryClient,
        setPage, 
        setLimit,
        productsData, 
        productIdData,
        productDetailsData,
        createMutation,
        updateMutation,
        deleteMutation,
        addDetailMutation,
        updateDetailMutation,
        deleteDetailMutation
    };
}