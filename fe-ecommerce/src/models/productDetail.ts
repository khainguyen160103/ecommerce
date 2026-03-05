export type ProductDetail = {
  id: string;
  product_id: string;
  size: string;
  color: string;
  stock: number;
  weight?: number;
  length?: number;
  width?: number;
  height?: number;
  create_at: string;
  update_at: string;
};

export type CreateProductDetailInput = {
  size: string;
  color: string;
  stock: number;
};

export type UpdateProductDetailInput = {
  size?: string;
  color?: string;
  stock?: number;
};
