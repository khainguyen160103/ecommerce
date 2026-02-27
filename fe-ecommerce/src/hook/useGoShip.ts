'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as goshipService from '@/requests/goship';
import { message } from 'antd';
import type { GoShipRateRequest, CreateShipmentRequest } from '@/requests/goship';

export const useGoShip = () => {
  const queryClient = useQueryClient();

  // Lấy danh sách tỉnh/thành phố
  const useGetCities = () => {
    return useQuery({
      queryKey: ['goship-cities'],
      queryFn: () => goshipService.getCities(),
      staleTime: 1000 * 60 * 60, // Cache 1 giờ
    });
  };

  // Lấy danh sách quận/huyện
  const useGetDistricts = (cityId?: number) => {
    return useQuery({
      queryKey: ['goship-districts', cityId],
      queryFn: () => goshipService.getDistricts(cityId!),
      enabled: !!cityId,
      staleTime: 1000 * 60 * 60,
    });
  };

  // Lấy danh sách phường/xã
  const useGetWards = (districtId?: number) => {
    return useQuery({
      queryKey: ['goship-wards', districtId],
      queryFn: () => goshipService.getWards(districtId!),
      enabled: !!districtId,
      staleTime: 1000 * 60 * 60,
    });
  };

  // Tính phí vận chuyển
  const useGetRates = (data?: GoShipRateRequest) => {
    return useQuery({
      queryKey: ['goship-rates', data?.to_city, data?.to_district],
      queryFn: () => goshipService.getRates(data!),
      enabled: !!data?.to_city && !!data?.to_district,
      staleTime: 1000 * 60 * 5,
    });
  };

  // Tạo đơn vận chuyển (Admin)
  const useCreateShipment = () => {
    return useMutation({
      mutationFn: (data: CreateShipmentRequest) =>
        goshipService.createShipment(data),
      onSuccess: () => {
        message.success('Tạo đơn vận chuyển GoShip thành công!');
        queryClient.invalidateQueries({ queryKey: ['allOrders'] });
      },
      onError: (error: any) => {
        message.error(
          error.response?.data?.detail || 'Lỗi tạo đơn vận chuyển'
        );
      },
    });
  };

  // Tracking đơn vận chuyển
  const useGetTracking = (orderId?: string) => {
    return useQuery({
      queryKey: ['goship-tracking', orderId],
      queryFn: () => goshipService.getTracking(orderId!),
      enabled: !!orderId,
      staleTime: 1000 * 60 * 2,
    });
  };

  // Hủy đơn vận chuyển (Admin)
  const useCancelShipment = () => {
    return useMutation({
      mutationFn: (orderId: string) => goshipService.cancelShipment(orderId),
      onSuccess: () => {
        message.success('Đã hủy đơn vận chuyển');
        queryClient.invalidateQueries({ queryKey: ['allOrders'] });
      },
      onError: (error: any) => {
        message.error(
          error.response?.data?.detail || 'Lỗi hủy đơn vận chuyển'
        );
      },
    });
  };

  return {
    useGetCities,
    useGetDistricts,
    useGetWards,
    useGetRates,
    useCreateShipment,
    useGetTracking,
    useCancelShipment,
  };
};
