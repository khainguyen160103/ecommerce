export type ProductImage = {
  id: string;
  product_id: string;
  cloudinary_public_id: string;
  url: string;
  thumbnail_url: string;
  created_at: string;
};

export type CreateProductImageInput = {
  cloudinary_public_id: string;
  url: string;
  thumbnail_url: string;
};
