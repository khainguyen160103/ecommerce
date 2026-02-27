import { ProductDetail } from './productDetail';
import { ProductImage } from './productImage';
import { Category } from './category';

export type Product = {
  id: string;
  name: string;
  description: string;
  price: string;
  category_id: string;
  create_at: string;
  update_at: string;
  category?: Category;
  details?: ProductDetail[];
  images?: ProductImage[];
};

export type ProductCard = Product & {
  images: ProductImage[];
};

export type CreateProductInput = {
  name: string;
  description: string;
  price: string;
  category_id: string;
};

export type UpdateProductInput = {
  name?: string;
  description?: string;
  price?: string;
  category_id?: string;
};
