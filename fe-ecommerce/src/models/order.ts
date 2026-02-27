import { OrderItem } from './orderItem';
import { User } from './user';

export type Order = {
  id: string;
  user_id: string;
  total: string;
  status: OrderStatus;
  create_at: string;
  update_at: string;
  user?: User;
  items_count: number;
  items?: OrderItem[];
};

export enum OrderStatus {
  PENDING = 'PENDING',
  CONFIRMED = 'CONFIRMED',
  SHIPPED = 'SHIPPED',
  DELIVERED = 'DELIVERED',
  CANCELLED = 'CANCELLED',
}

export type CreateOrderInput = {
  items: CreateOrderItemInput[];
  address_id: string;
};

export type CreateOrderItemInput = {
  product_detail_id: string;
  quantity: number;
};

export type UpdateOrderInput = {
  status?: OrderStatus;
};
