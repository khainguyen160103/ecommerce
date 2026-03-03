export type ProductDetail = {
  id: string;
  product_id: string;
  sku: string;
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
  sku: string;
  size: string;
  color: string;
  stock: number;
};

export type UpdateProductDetailInput = {
  sku?: string;
  size?: string;
  color?: string;
  stock?: number;
};
