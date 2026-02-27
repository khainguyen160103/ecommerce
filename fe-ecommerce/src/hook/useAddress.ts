'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as addressService from '@/requests/address';
import { message } from 'antd';

export const useAddress = () => {
  const queryClient = useQueryClient();

  const useGetMyAddresses = () => {
    return useQuery({
      queryKey: ['myAddresses'],
      queryFn: () => addressService.getMyAddresses(),
      staleTime: 1000 * 60 * 5,
    });
  };

  const useCreateAddress = () => {
    return useMutation({
      mutationFn: (data: {
        title?: string;
        address: string;
        phone_number?: string;
        city_id?: number;
        district_id?: number;
        ward_id?: number;
        city_name?: string;
        district_name?: string;
        ward_name?: string;
      }) => addressService.createAddress(data),
      onSuccess: () => {
        message.success('Thêm địa chỉ thành công!');
        queryClient.invalidateQueries({ queryKey: ['myAddresses'] });
      },
      onError: (error: any) => {
        message.error(
          error.response?.data?.detail || 'Không thể thêm địa chỉ'
        );
      },
    });
  };

  const useUpdateAddress = () => {
    return useMutation({
      mutationFn: ({
        addressId,
        data,
      }: {
        addressId: string;
        data: { title?: string; address?: string; phone_number?: string };
      }) => addressService.updateAddress(addressId, data),
      onSuccess: () => {
        message.success('Cập nhật địa chỉ thành công!');
        queryClient.invalidateQueries({ queryKey: ['myAddresses'] });
      },
      onError: (error: any) => {
        message.error(
          error.response?.data?.detail || 'Không thể cập nhật địa chỉ'
        );
      },
    });
  };

  return {
    useGetMyAddresses,
    useCreateAddress,
    useUpdateAddress,
  };
};
