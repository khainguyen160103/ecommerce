export type Address = {
  id: string;
  user_id: string;
  name: string;
  phone_number: string;
  address: string;
  create_at: string;
  update_at: string;
};

export type CreateAddressInput = {
  name: string;
  phone_number: string;
  address: string;
};

export type UpdateAddressInput = {
  name?: string;
  phone_number?: string;
  address?: string;
};
