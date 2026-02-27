import { axiosClient } from './index';
import { ENDPOINT } from './endpoint';

// ==================== TYPES ====================

export interface GoShipCity {
  id: number;
  name: string;
}

export interface GoShipDistrict {
  id: number;
  name: string;
  city_id: number;
}

export interface GoShipWard {
  id: number;
  name: string;
  district_id: number;
}

export interface GoShipRate {
  id: string;
  name?: string;
  carrier?: string;
  carrier_name?: string;
  carrier_logo?: string;
  service?: string;
  estimated_days?: string;
  estimated_pick_time?: string;
  estimated_deliver_time?: string;
  fee: number;
}

export interface GoShipRateRequest {
  to_city: number;
  to_district: number;
  cod?: number;
  amount?: number;
  weight?: number;
}

export interface CreateShipmentRequest {
  order_id: string;
  rate_id: string;
}

export interface ShipmentTracking {
  order_id: string;
  status: string;
  shipping_code?: string;
  tracking_number?: string;
  carrier?: string;
  tracking?: any;
}

// ==================== API CALLS ====================

// Lấy danh sách tỉnh/thành phố
export const getCities = async (): Promise<GoShipCity[]> => {
  const response = await axiosClient.get(ENDPOINT.GOSHIP.CITIES);
  return response.data?.data || response.data || [];
};

// Lấy danh sách quận/huyện theo tỉnh/thành
export const getDistricts = async (cityId: number): Promise<GoShipDistrict[]> => {
  const response = await axiosClient.get(ENDPOINT.GOSHIP.DISTRICTS(cityId));
  return response.data?.data || response.data || [];
};

// Lấy danh sách phường/xã theo quận/huyện
export const getWards = async (districtId: number): Promise<GoShipWard[]> => {
  const response = await axiosClient.get(ENDPOINT.GOSHIP.WARDS(districtId));
  return response.data?.data || response.data || [];
};

// Tính phí vận chuyển từ GoShip
export const getRates = async (data: GoShipRateRequest): Promise<GoShipRate[]> => {
  const response = await axiosClient.post(ENDPOINT.GOSHIP.RATES, data);
  return response.data?.data || response.data || [];
};

// Tạo đơn vận chuyển GoShip (Admin)
export const createShipment = async (data: CreateShipmentRequest) => {
  const response = await axiosClient.post(ENDPOINT.GOSHIP.CREATE_SHIPMENT, data);
  return response.data;
};

// Tracking đơn vận chuyển
export const getTracking = async (orderId: string): Promise<ShipmentTracking> => {
  const response = await axiosClient.get(ENDPOINT.GOSHIP.TRACKING(orderId));
  return response.data;
};

// Hủy đơn vận chuyển (Admin)
export const cancelShipment = async (orderId: string) => {
  const response = await axiosClient.patch(ENDPOINT.GOSHIP.CANCEL_SHIPMENT(orderId));
  return response.data;
};
