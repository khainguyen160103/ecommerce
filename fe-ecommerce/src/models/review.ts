export type Review = {
  id: string;
  product_id: string;
  user_id: string;
  rating: number;
  comment: string | null;
  username: string;
  create_at: string;
  update_at: string;
};

export type ReviewSummary = {
  avg_rating: number;
  total_reviews: number;
  distribution: Record<number, number>; // { 1: 5, 2: 3, 3: 10, ... }
};

export type ReviewListResponse = {
  data: Review[];
  summary: ReviewSummary;
  pagination: {
    page: number;
    pageSize: number;
    total_item: number;
    totalPages: number;
  };
};

export type CreateReviewInput = {
  rating: number;
  comment?: string;
};

export type UpdateReviewInput = {
  rating?: number;
  comment?: string;
};
