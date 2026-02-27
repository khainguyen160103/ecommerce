export type User = {
  id: string;
  name: string;
  email: string;
  password_hash?: string;
  phone_number: string;
  create_at: string;
  update_at: string;
};

export type CreateUserInput = {
  name: string;
  email: string;
  password: string;
  phone_number: string;
};

export type UpdateUserInput = {
  name?: string;
  email?: string;
  phone_number?: string;
};
