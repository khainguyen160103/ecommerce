import { ProductDetail } from './productDetail';

export type CartItem = {
  id: string;
  user_id: string;
  product_detail_id: string;
  quantity: number;
  create_at: string;
  update_at: string;
  product_detail?: ProductDetail;
};

export type CreateCartItemInput = {
  product_detail_id: string;
  quantity: number;
};

export type UpdateCartItemInput = {
  quantity: number;
};
