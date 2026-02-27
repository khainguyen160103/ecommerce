import { axiosClient } from './index';
import { ENDPOINT } from './endpoint';

// Lấy danh sách địa chỉ của user
export const getMyAddresses = async () => {
  const response = await axiosClient.get(ENDPOINT.ADDRESS.GET_MY_ADDRESSES);
  return response.data;
};

// Tạo địa chỉ mới
export const createAddress = async (data: {
  title?: string;
  address: string;
  phone_number?: string;
  city_id?: number;
  district_id?: number;
  ward_id?: number;
  city_name?: string;
  district_name?: string;
  ward_name?: string;
}) => {
  const response = await axiosClient.post(ENDPOINT.ADDRESS.CREATE, data);
  return response.data;
};

// Cập nhật địa chỉ
export const updateAddress = async (
  addressId: string,
  data: {
    title?: string;
    address?: string;
    phone_number?: string;
    city_id?: number;
    district_id?: number;
    ward_id?: number;
    city_name?: string;
    district_name?: string;
    ward_name?: string;
  }
) => {
  const response = await axiosClient.put(
    ENDPOINT.ADDRESS.UPDATE(addressId),
    data
  );
  return response.data;
};
