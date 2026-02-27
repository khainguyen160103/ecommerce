import { ProductDetail } from './productDetail';

export type OrderItem = {
  id: string;
  order_id: string;
  product_detail_id: string;
  quantity: number;
  create_at: string;
  update_at: string;
  product_detail?: ProductDetail;
};

export type CreateOrderItemInput = {
  product_detail_id: string;
  quantity: number;
};
