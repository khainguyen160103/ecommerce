export type Images = {
  cloudinary_id: string;
  url: string;
};
export type Product = {
  id: string;
  name: string;
  description: string;
  price: string;
  category_id: string;
  create_at: string;
  update_at : string;
  images: [Images];
};
export type DataType = Omit<Product, "images">

export type ProductDetail = {
  id: string;
  product_id: string;
  color?: string;
  size?: string;
  stock: number;
  weight?: number;
  length?: number;
  width?: number;
  height?: number;
  create_at: string;
  update_at: string;
}

export interface CategoryOption {
  label: string;
  value: string;
}