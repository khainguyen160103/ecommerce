import { axiosClient } from './index';
import { ENDPOINT } from './endpoint';

export interface CheckoutRequest {
  payment_method: 'vnpay' | 'cod';
  address_id?: string;
  shipping_method?: string;
  note?: string;
  rate_id?: string;
  shipping_fee?: number;
  item_ids?: string[];
}

export interface CheckoutResponse {
  message: string;
  order_id: string;
  payment_method: string;
  payment_url?: string; // Only for VNPay
  total: number;
}

export interface ShippingRate {
  id: string;
  name: string;
  carrier: string;
  carrier_logo?: string;
  estimated_days: string;
  fee: number;
}

export interface ShippingRatesResponse {
  rates: ShippingRate[];
}

export interface OrderPreview {
  items: {
    id: string;
    product_id: string;
    detail_id: string;
    product_name: string;
    price: number;
    quantity: number;
    item_total: number;
  }[];
  subtotal: number;
  shipping_fee: number;
  total: number;
  address: {
    id: string;
    title: string;
    address: string;
    phone_number: string;
  } | null;
  items_count: number;
}

export interface VNPayReturnResult {
  success: boolean;
  message: string;
  order_id?: string;
  amount?: number;
  transaction_no?: string;
  bank_code?: string;
  response_code?: string;
}

// Xem trước đơn hàng
export const getOrderPreview = async (itemIds?: string[]): Promise<OrderPreview> => {
  const params = itemIds && itemIds.length > 0 ? `?item_ids=${itemIds.join(',')}` : '';
  const response = await axiosClient.get(`${ENDPOINT.CHECKOUT.ORDER_PREVIEW}${params}`);
  return response.data;
};

// Tạo checkout
export const createCheckout = async (
  data: CheckoutRequest
): Promise<CheckoutResponse> => {
  const response = await axiosClient.post(ENDPOINT.CHECKOUT.CREATE, data);
  return response.data;
};

// Lấy shipping rates
export const getShippingRates = async (
  addressId: string,
  weight?: number
): Promise<ShippingRatesResponse> => {
  const response = await axiosClient.post(ENDPOINT.CHECKOUT.SHIPPING_RATES, {
    address_id: addressId,
    weight: weight || 500,
  });
  return response.data;
};

// Verify VNPay return
export const verifyVNPayReturn = async (
  params: string
): Promise<VNPayReturnResult> => {
  const response = await axiosClient.get(
    `${ENDPOINT.CHECKOUT.VNPAY_RETURN}?${params}`
  );
  return response.data;
};
