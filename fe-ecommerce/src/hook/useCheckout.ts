'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as checkoutService from '@/requests/checkout';
import { message } from 'antd';
import type { CheckoutRequest } from '@/requests/checkout';

export const useCheckout = () => {
  const queryClient = useQueryClient();

  // Xem trước đơn hàng
  const useOrderPreview = (itemIds?: string[]) => {
    return useQuery({
      queryKey: ['orderPreview', itemIds],
      queryFn: () => checkoutService.getOrderPreview(itemIds),
      enabled: !itemIds || itemIds.length > 0,
      staleTime: 1000 * 60 * 2,
    });
  };

  // Tạo checkout (COD hoặc VNPay)
  const useCreateCheckout = () => {
    return useMutation({
      mutationFn: (data: CheckoutRequest) =>
        checkoutService.createCheckout(data),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['myCart'] });
        queryClient.invalidateQueries({ queryKey: ['myOrders'] });
        queryClient.invalidateQueries({ queryKey: ['orderPreview'] });
      },
      onError: (error: any) => {
        message.error(
          error.response?.data?.detail || 'Không thể tạo đơn hàng'
        );
      },
    });
  };

  // Lấy phí vận chuyển
  const useShippingRates = (addressId: string, weight?: number) => {
    return useQuery({
      queryKey: ['shippingRates', addressId, weight],
      queryFn: () => checkoutService.getShippingRates(addressId, weight),
      enabled: !!addressId,
      staleTime: 1000 * 60 * 5,
    });
  };

  // Verify VNPay return
  const useVerifyVNPay = () => {
    return useMutation({
      mutationFn: (params: string) =>
        checkoutService.verifyVNPayReturn(params),
      onSuccess: (data) => {
        if (data.success) {
          message.success(data.message);
        } else {
          message.error(data.message);
        }
        queryClient.invalidateQueries({ queryKey: ['myOrders'] });
      },
    });
  };

  return {
    useOrderPreview,
    useCreateCheckout,
    useShippingRates,
    useVerifyVNPay,
  };
};
