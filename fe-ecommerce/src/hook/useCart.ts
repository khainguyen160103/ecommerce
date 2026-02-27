'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as cartService from '@/requests/cart';
import { message } from 'antd';
import { Authorization } from '@/utils/auth.utils';

export const useCart = () => {
  const queryClient = useQueryClient();

  // Get my cart
  const useGetMyCart = () => {
    const token = Authorization.getToken();
    return useQuery({
      queryKey: ['myCart'],
      queryFn: () => cartService.getMyCart(),
      staleTime: 1000 * 60 * 5, // 5 minutes
      enabled: !!token, // Chỉ chạy query nếu token tồn tại
    });
  };

  // Add item to cart
  const useAddToCart = () => {
    return useMutation({
      mutationFn: (data: cartService.AddToCartRequest) => cartService.addToCart(data),
      onSuccess: (data) => {
        message.success('Đã thêm sản phẩm vào giỏ hàng!');
        queryClient.setQueryData(['myCart'], data);
        queryClient.invalidateQueries({ queryKey: ['myCart'] });
        return data;
      },
      onError: (error: any) => {
        const errorMessage = error.response?.data?.detail || 'Không thể thêm sản phẩm vào giỏ hàng';
        message.error(errorMessage);
      },
    });
  };

  // Update cart item quantity
  const useUpdateCartItem = () => {
    return useMutation({
      mutationFn: ({
        itemId,
        quantity,
      }: {
        itemId: string;
        quantity: number;
      }) => cartService.updateCartItem(itemId, { quantity }),
      onSuccess: (data) => {
        message.success('Cập nhật giỏ hàng thành công!');
        queryClient.setQueryData(['myCart'], data);
        queryClient.invalidateQueries({ queryKey: ['myCart'] });
        return data;
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || 'Không thể cập nhật giỏ hàng');
      },
    });
  };

  // Delete cart item
  const useDeleteCartItem = () => {
    return useMutation({
      mutationFn: (itemId: string) => cartService.deleteCartItem(itemId),
      onSuccess: (data) => {
        message.success('Đã xóa sản phẩm khỏi giỏ hàng!');
        queryClient.setQueryData(['myCart'], data);
        queryClient.invalidateQueries({ queryKey: ['myCart'] });
        return data;
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || 'Không thể xóa sản phẩm');
      },
    });
  };

  // Clear cart
  const useClearCart = () => {
    return useMutation({
      mutationFn: () => cartService.clearCart(),
      onSuccess: () => {
        message.success('Đã xóa tất cả sản phẩm khỏi giỏ hàng!');
        queryClient.setQueryData(['myCart'], { items: [], total: 0 });
        queryClient.invalidateQueries({ queryKey: ['myCart'] });
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || 'Không thể xóa giỏ hàng');
      },
    });
  };

  return {
    useGetMyCart,
    useAddToCart,
    useUpdateCartItem,
    useDeleteCartItem,
    useClearCart,
  };
};
