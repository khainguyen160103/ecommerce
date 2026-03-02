export type Cart = {
  product_id: string;
  quantity: number;
  detail_id: string;
  cart_id: string;
};

export type CartItem = {};
export interface CartItemRaw {
  id?: string;
  product_id?: string;
  detail_id?: string;
  productDetailId?: string;
  color?: string;
  size?: string;
  quantity: number;
  price?: number;
  image?: string;
  product_name?: string;
}
