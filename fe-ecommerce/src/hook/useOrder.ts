'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as orderService from '@/requests/order';
import { message } from 'antd';

export const useOrder = () => {
  const queryClient = useQueryClient();

  // Get User's Orders
  const useGetMyOrders = (skip: number = 0, limit: number = 100) => {
    return useQuery({
      queryKey: ['myOrders', skip, limit],
      queryFn: () => orderService.getMyOrders(skip, limit),
      staleTime: 1000 * 60 * 5, // 5 minutes
    });
  };

  // Get Order By ID
  const useGetMyOrderById = (orderId: string) => {
    return useQuery({
      queryKey: ['myOrder', orderId],
      queryFn: () => orderService.getMyOrderById(orderId),
      enabled: !!orderId,
      staleTime: 1000 * 60 * 5,
    });
  };

  // Create Order from Cart
  const useCreateOrderFromCart = () => {
    return useMutation({
      mutationFn: () => orderService.createOrderFromCart(),
      onSuccess: (data) => {
        message.success('Đơn hàng đã được tạo thành công!');
        queryClient.invalidateQueries({ queryKey: ['myOrders'] });
        return data;
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || 'Không thể tạo đơn hàng');
      },
    });
  };

  // Cancel Order
  const useCancelOrder = () => {
    return useMutation({
      mutationFn: (orderId: string) => orderService.cancelMyOrder(orderId),
      onSuccess: (data, orderId) => {
        message.success('Đơn hàng đã được hủy!');
        queryClient.invalidateQueries({ queryKey: ['myOrders'] });
        queryClient.invalidateQueries({ queryKey: ['myOrder', orderId] });
        return data;
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || 'Không thể hủy đơn hàng');
      },
    });
  };

  // Admin: Get All Orders
  const useGetAllOrders = (skip: number = 0, limit: number = 100, statusFilter?: string) => {
    return useQuery({
      queryKey: ['allOrders', skip, limit, statusFilter],
      queryFn: () => orderService.getAllOrders(skip, limit, statusFilter),
      staleTime: 1000 * 60 * 5,
    });
  };

  // Admin: Get Order By ID
  const useGetOrderByIdAdmin = (orderId: string) => {
    return useQuery({
      queryKey: ['order', orderId],
      queryFn: () => orderService.getOrderById(orderId),
      enabled: !!orderId,
      staleTime: 1000 * 60 * 5,
    });
  };

  // Admin: Update Order Status
  const useUpdateOrderStatus = () => {
    return useMutation({
      mutationFn: ({ orderId, status }: { orderId: string; status: string }) =>
        orderService.updateOrderStatus(orderId, status),
      onSuccess: (data, { orderId }) => {
        message.success('Cập nhật trạng thái đơn hàng thành công!');
        queryClient.invalidateQueries({ queryKey: ['allOrders'] });
        queryClient.invalidateQueries({ queryKey: ['order', orderId] });
        return data;
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || 'Không thể cập nhật trạng thái đơn hàng');
      },
    });
  };

  return {
    // User hooks
    useGetMyOrders,
    useGetMyOrderById,
    useCreateOrderFromCart,
    useCancelOrder,
    // Admin hooks
    useGetAllOrders,
    useGetOrderByIdAdmin,
    useUpdateOrderStatus,
  };
};
