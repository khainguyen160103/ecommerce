export type Discount = {
  id: string;
  code: string;
  description: string | null;
  discount_type: "percent" | "fixed";
  discount_value: number;
  min_order_value: number;
  max_discount: number | null;
  usage_limit: number | null;
  used_count: number;
  is_active: boolean;
  start_date: string | null;
  end_date: string | null;
  create_at: string;
  update_at: string;
};

export type CreateDiscountInput = {
  code: string;
  description?: string;
  discount_type: "percent" | "fixed";
  discount_value: number;
  min_order_value?: number;
  max_discount?: number | null;
  usage_limit?: number | null;
  is_active?: boolean;
  start_date?: string | null;
  end_date?: string | null;
};

export type UpdateDiscountInput = Partial<CreateDiscountInput>;

export type ApplyDiscountResult = {
  discount_id: string;
  code: string;
  discount_type: "percent" | "fixed";
  discount_value: number;
  discount_amount: number;
  max_discount: number | null;
  message: string;
};
