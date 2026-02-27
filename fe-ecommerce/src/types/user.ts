export type User = {
  username: string | null;
  email: string;
  id: string;
  status: boolean;
  password_hashed?: string;
  create_at: string;
  update_at: string;
  role: string
};
export type UserInfor = Omit<User, 'password_hashed'>