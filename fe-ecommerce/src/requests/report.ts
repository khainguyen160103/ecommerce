/**
 * Report API - Báo cáo doanh thu
 */
import { axiosClient } from '.';

export interface RevenueData {
  total_orders: number;
  total_revenue: number;
  avg_order_value: number;
}

export interface DailyData {
  date: string;
  total_orders: number;
  revenue: number;
}

export interface MonthlyData {
  month: number;
  total_orders: number;
  revenue: number;
}

export interface TopProduct {
  product_id: string;
  product_name: string;
  total_quantity: number;
  total_orders: number;
}

export interface StatusSummary {
  status: string;
  total_orders: number;
  total_value: number;
}

export interface DashboardResponse {
  period: string;
  start_date: string;
  end_date: string;
  revenue: RevenueData;
  top_products: TopProduct[];
  status_summary: StatusSummary[];
}

export interface DailyRevenueResponse {
  year: number;
  month: number;
  total_revenue: number;
  total_orders: number;
  daily_data: DailyData[];
}

export interface MonthlyRevenueResponse {
  year: number;
  total_revenue: number;
  total_orders: number;
  monthly_data: MonthlyData[];
}

export interface CustomReportResponse {
  start_date: string;
  end_date: string;
  revenue: RevenueData;
  top_products: TopProduct[];
  status_summary: StatusSummary[];
}

export const reportAPI = {
  /**
   * Lấy dashboard tổng quan
   */
  getDashboard: async (period: 'today' | 'week' | 'month' | 'year' = 'month'): Promise<DashboardResponse> => {
    const response = await axiosClient.get(`/reports/dashboard?period=${period}`);
    return response.data;
  },

  /**
   * Lấy doanh thu theo ngày
   */
  getDailyRevenue: async (year: number, month: number): Promise<DailyRevenueResponse> => {
    const response = await axiosClient.get(`/reports/revenue/daily?year=${year}&month=${month}`);
    return response.data;
  },

  /**
   * Lấy doanh thu theo tháng
   */
  getMonthlyRevenue: async (year: number): Promise<MonthlyRevenueResponse> => {
    const response = await axiosClient.get(`/reports/revenue/monthly?year=${year}`);
    return response.data;
  },

  /**
   * Lấy báo cáo tùy chỉnh
   */
  getCustomReport: async (startDate: string, endDate: string): Promise<CustomReportResponse> => {
    const response = await axiosClient.get(
      `/reports/revenue/custom?start_date=${startDate}&end_date=${endDate}`
    );
    return response.data;
  },
};
