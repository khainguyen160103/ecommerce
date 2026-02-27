export type PaymentDetail = {
  id: string;
  order_id: string;
  processor_id: string;
  status: PaymentStatus;
  create_at: string;
  update_at: string;
};

export enum PaymentStatus {
  PENDING = 'PENDING',
  PROCESSING = 'PROCESSING',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  REFUNDED = 'REFUNDED',
}

export type CreatePaymentInput = {
  order_id: string;
  processor_id: string;
};

export type UpdatePaymentInput = {
  status?: PaymentStatus;
};
