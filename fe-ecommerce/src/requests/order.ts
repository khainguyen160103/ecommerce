import { axiosClient } from './index';
import { ENDPOINT } from './endpoint';

// User Order Endpoints
export const getMyOrders = async (skip: number = 0, limit: number = 100) => {
  const response = await axiosClient.get(ENDPOINT.ORDER.GET_MY_ORDERS, {
    params: { skip, limit },
  });
  return response.data;
};

export const getMyOrderById = async (orderId: string) => {
  const response = await axiosClient.get(ENDPOINT.ORDER.GET_MY_ORDER_BY_ID(orderId));
  return response.data;
};

export const createOrderFromCart = async () => {
  const response = await axiosClient.post(ENDPOINT.ORDER.CREATE_ORDER);
  return response.data;
};

export const cancelMyOrder = async (orderId: string) => {
  const response = await axiosClient.post(ENDPOINT.ORDER.CANCEL_ORDER(orderId));
  return response.data;
};

// Admin Order Endpoints
export const getAllOrders = async (skip: number = 0, limit: number = 100, statusFilter?: string) => {
  const response = await axiosClient.get(ENDPOINT.ORDER.GET_ALL_ORDERS, {
    params: { skip, limit, status_filter: statusFilter },
  });
  return response.data;
};

export const getOrderById = async (orderId: string) => {
  const response = await axiosClient.get(ENDPOINT.ORDER.GET_ORDER_BY_ID(orderId));
  return response.data;
};

export const updateOrderStatus = async (orderId: string, status: string) => {
  const response = await axiosClient.patch(ENDPOINT.ORDER.UPDATE_ORDER_STATUS(orderId), {
    status,
  });
  return response.data;
};
