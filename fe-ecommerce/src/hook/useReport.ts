/**
 * useReport Hook - Hook để lấy báo cáo doanh thu
 */
import { useQuery } from '@tanstack/react-query';
import { reportAPI } from '@/requests/report';

export const useReport = () => {
  /**
   * Dashboard tổng quan
   */
  const useDashboard = (period: 'today' | 'week' | 'month' | 'year' = 'month') => {
    return useQuery({
      queryKey: ['dashboard', period],
      queryFn: () => reportAPI.getDashboard(period),
    });
  };

  /**
   * Doanh thu theo ngày
   */
  const useDailyRevenue = (year: number, month: number) => {
    return useQuery({
      queryKey: ['dailyRevenue', year, month],
      queryFn: () => reportAPI.getDailyRevenue(year, month),
      enabled: !!year && !!month,
    });
  };

  /**
   * Doanh thu theo tháng
   */
  const useMonthlyRevenue = (year: number) => {
    return useQuery({
      queryKey: ['monthlyRevenue', year],
      queryFn: () => reportAPI.getMonthlyRevenue(year),
      enabled: !!year,
    });
  };

  /**
   * Báo cáo tùy chỉnh
   */
  const useCustomReport = (startDate: string, endDate: string) => {
    return useQuery({
      queryKey: ['customReport', startDate, endDate],
      queryFn: () => reportAPI.getCustomReport(startDate, endDate),
      enabled: !!startDate && !!endDate,
    });
  };

  return {
    useDashboard,
    useDailyRevenue,
    useMonthlyRevenue,
    useCustomReport,
  };
};
