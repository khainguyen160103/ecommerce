export type Category = {
  id: string;
  name: string;
  description: string;
  create_at: string;
  update_at: string;
};

export type CreateCategoryInput = {
  name: string;
  description: string;
};

export type UpdateCategoryInput = {
  name?: string;
  description?: string;
};
