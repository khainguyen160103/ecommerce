import { axiosClient } from "./index";
import { ENDPOINT } from "./endpoint";
import { Cart } from "@/models/cart";
export interface AddToCartRequest {
  product_id?: string;
  detail_id: string;
  quantity: number;
  cart_id?: string;
}

export interface UpdateCartItemRequest {
  quantity: number;
}

export interface CartItem {
  cart_id: string;
  create_at: string;
  detail_id: string;
  id: string;
  product_id: string;
  quantity: number;
  update_at: string;
}

export interface CartResponse {
  cart: {
    create_at: string;
    update_at: string;
    total: number;
    user_id: string;
    id: string;
  };
  items: CartItem[];
  total_items: number;
}

// Get my cart
export const getMyCart = async (): Promise<CartResponse> => {
  const response = await axiosClient.get(ENDPOINT.CART.GET_MY_CART);
  return response.data;
};

// Add item to cart
export const addToCart = async (
  data: AddToCartRequest,
): Promise<CartResponse> => {
  const response = await axiosClient.post(ENDPOINT.CART.ADD_ITEM, data);
  return response.data;
};

// Update cart item quantity
export const updateCartItem = async (
  itemId: string,
  data: UpdateCartItemRequest,
): Promise<CartResponse> => {
  const response = await axiosClient.patch(
    ENDPOINT.CART.UPDATE_ITEM(itemId),
    data,
  );
  return response.data;
};

// Delete cart item
export const deleteCartItem = async (itemId: string): Promise<CartResponse> => {
  const response = await axiosClient.delete(ENDPOINT.CART.DELETE_ITEM(itemId));
  return response.data;
};

// Clear cart
export const clearCart = async (): Promise<{ message: string }> => {
  const response = await axiosClient.delete(ENDPOINT.CART.CLEAR_CART);
  return response.data;
};
