'use client';

import React, { useState } from 'react';
import { useReport } from '@/hook/useReport';
import { Card, Col, Row, Select, Space, Spin, Statistic, Table, Tabs, Tag, Typography } from 'antd';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bar, Line, Pie } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

export default function ReportsPage() {
  const [period, setPeriod] = useState<'today' | 'week' | 'month' | 'year'>('month');
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [viewMode, setViewMode] = useState<'dashboard' | 'daily' | 'monthly'>('dashboard');

  const { useDashboard, useDailyRevenue, useMonthlyRevenue } = useReport();
  
  const { data: dashboardData, isLoading: isDashboardLoading } = useDashboard(period);
  const { data: dailyData, isLoading: isDailyLoading } = useDailyRevenue(
    selectedYear,
    selectedMonth
  );
  const { data: monthlyData, isLoading: isMonthlyLoading } = useMonthlyRevenue(selectedYear);

  // Format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND',
    }).format(amount);
  };

  // Get status label in Vietnamese
  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      pending: 'Chờ xác nhận',
      confirmed: 'Đã xác nhận',
      shipping: 'Đang giao',
      delivered: 'Đã giao',
      cancelled: 'Đã hủy',
    };
    return labels[status] || status;
  };

  const getStatusTagColor = (status: string): string => {
    const colors: Record<string, string> = {
      pending: 'gold',
      confirmed: 'blue',
      shipping: 'purple',
      delivered: 'green',
      cancelled: 'red',
    };
    return colors[status] || 'default';
  };

  const yearOptions = [...Array(5)].map((_, i) => {
    const year = new Date().getFullYear() - i;
    return { value: year, label: String(year) };
  });

  const monthOptions = [...Array(12)].map((_, i) => {
    const m = i + 1;
    return { value: m, label: `Tháng ${m}` };
  });

  // Chart data for daily revenue
  const dailyChartData = dailyData
    ? {
        labels: dailyData.daily_data.map((d) => d.date.split('-')[2]), // Chỉ lấy ngày
        datasets: [
          {
            label: 'Doanh thu (VNĐ)',
            data: dailyData.daily_data.map((d) => d.revenue),
            backgroundColor: 'rgba(59, 130, 246, 0.5)',
            borderColor: 'rgb(59, 130, 246)',
            borderWidth: 2,
          },
        ],
      }
    : null;

  // Chart data for monthly revenue
  const monthlyChartData = monthlyData
    ? {
        labels: monthlyData.monthly_data.map((d) => `Tháng ${d.month}`),
        datasets: [
          {
            label: 'Doanh thu (VNĐ)',
            data: monthlyData.monthly_data.map((d) => d.revenue),
            backgroundColor: 'rgba(34, 197, 94, 0.5)',
            borderColor: 'rgb(34, 197, 94)',
            borderWidth: 2,
            tension: 0.4,
          },
        ],
      }
    : null;

  // Chart data for order status
  const statusChartData = dashboardData
    ? {
        labels: dashboardData.status_summary.map((s) => getStatusLabel(s.status)),
        datasets: [
          {
            data: dashboardData.status_summary.map((s) => s.total_orders),
            backgroundColor: [
              'rgba(234, 179, 8, 0.6)',
              'rgba(59, 130, 246, 0.6)',
              'rgba(168, 85, 247, 0.6)',
              'rgba(34, 197, 94, 0.6)',
              'rgba(239, 68, 68, 0.6)',
            ],
            borderWidth: 0,
          },
        ],
      }
    : null;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <Space orientation="vertical" size={16} style={{ width: '100%' }}>
          <div>
            <Typography.Title level={2} style={{ marginBottom: 0 }}>
              📊 Báo cáo Doanh thu
            </Typography.Title>
            <Typography.Paragraph style={{ marginTop: 8, color: '#6b7280' }}>
              Thống kê và phân tích doanh số bán hàng
            </Typography.Paragraph>
          </div>

          <Card variant="borderless" style={{ paddingTop: 4 }}>
            <Tabs
              activeKey={viewMode}
              onChange={(key) => setViewMode(key as typeof viewMode)}
              items={[
                { key: 'dashboard', label: 'Dashboard' },
                { key: 'daily', label: 'Theo Ngày' },
                { key: 'monthly', label: 'Theo Tháng' },
              ]}
            />

            {/* Dashboard View */}
            {viewMode === 'dashboard' && (
              <Space orientation="vertical" size={16} style={{ width: '100%' }}>
                <Card variant="borderless" style={{ marginBottom: 16 }}>
                  <div style={{ marginBottom: 12 }}>
                    <Typography.Text strong style={{ display: 'block', marginBottom: 8 }}>Khoảng thời gian:</Typography.Text>
                    <Tabs
                      size="small"
                      activeKey={period}
                      onChange={(key) => setPeriod(key as typeof period)}
                      items={[
                        { key: 'today', label: 'Hôm nay' },
                        { key: 'week', label: 'Tuần này' },
                        { key: 'month', label: 'Tháng này' },
                        { key: 'year', label: 'Năm này' },
                      ]}
                    />
                  </div>
                </Card>

                {isDashboardLoading ? (
                  <div className="text-center py-12">
                    <Spin size="large" />
                  </div>
                ) : dashboardData ? (
                  <>
                    <Row gutter={[16, 16]}>
                      <Col xs={24} md={8}>
                        <Card
                          variant="borderless"
                          className="bg-gradient-to-br from-blue-500 to-blue-600"
                          styles={{ body: { color: 'black', padding: '20px' } }}
                        >
                          <Statistic
                            title={<span style={{ color: 'black' }}>Tổng Doanh Thu</span>}
                            value={formatCurrency(dashboardData.revenue.total_revenue)}
                            styles={{ content: { color: 'black', fontWeight: 700, fontSize: '20px' } }}
                          />
                          <Typography.Text style={{ color: 'black', display: 'block', marginTop: 8 }}>
                            {dashboardData.revenue.total_orders} đơn hàng
                          </Typography.Text>
                        </Card>
                      </Col>

                      <Col xs={24} md={8}>
                        <Card
                          variant="borderless"
                          className="bg-gradient-to-br from-green-500 to-green-600"
                          styles={{ body: { color: 'black', padding: '20px' } }}
                        >
                          <Statistic
                              title={<span style={{ color: 'black' }}>Giá Trị TB/Đơn</span>}
                            value={formatCurrency(dashboardData.revenue.avg_order_value)}
                            styles={{ content: { color: 'black', fontWeight: 700, fontSize: '20px' } }}
                          />
                            <Typography.Text style={{ color: 'black', display: 'block', marginTop: 8 }}>
                            Trung bình mỗi đơn
                          </Typography.Text>
                        </Card>
                      </Col>

                      <Col xs={24} md={8}>
                        <Card
                          variant="borderless"
                          className="bg-gradient-to-br from-purple-500 to-purple-600"
                          styles={{ body: { color: 'black', padding: '20px' } }}
                        >
                          <Statistic
                              title={<span style={{ color: 'black' }}>Tổng Đơn Hàng</span>}
                            value={dashboardData.revenue.total_orders}
                            styles={{ content: { color: 'black', fontWeight: 700, fontSize: '20px' } }}
                          />
                            <Typography.Text style={{ color: 'black', display: 'block', marginTop: 8, fontSize: '12px' }}>
                            Từ {dashboardData.start_date} đến {dashboardData.end_date}
                          </Typography.Text>
                        </Card>
                      </Col>
                    </Row>

                    <Row gutter={[16, 16]}>
                      <Col xs={24} lg={12}>
                        <Card title="🏆 Sản Phẩm Bán Chạy" variant="borderless">
                          <Table
                            size="middle"
                            pagination={false}
                            rowKey="product_id"
                            dataSource={dashboardData.top_products}
                            columns={[
                              {
                                title: '#',
                                dataIndex: 'index',
                                key: 'index',
                                width: 60,
                                render: (_: unknown, __: unknown, index: number) => (
                                  <Tag color="blue">{index + 1}</Tag>
                                ),
                              },
                              {
                                title: 'Sản phẩm',
                                dataIndex: 'product_name',
                                key: 'product_name',
                                render: (name: string, record: any) => (
                                  <div>
                                    <Typography.Text strong>{name}</Typography.Text>
                                    <div style={{ color: '#6b7280' }}>{record.total_orders} đơn</div>
                                  </div>
                                ),
                              },
                              {
                                title: 'Số lượng',
                                dataIndex: 'total_quantity',
                                key: 'total_quantity',
                                align: 'right',
                                render: (qty: number) => (
                                  <Typography.Text strong style={{ color: '#1677ff' }}>
                                    {qty}
                                  </Typography.Text>
                                ),
                              },
                            ]}
                          />
                        </Card>
                      </Col>

                      <Col xs={24} lg={12}>
                        <Card title="📦 Trạng Thái Đơn Hàng" variant="borderless">
                          {statusChartData && (
                            <div className="h-64">
                              <Pie data={statusChartData} options={{ maintainAspectRatio: false }} />
                            </div>
                          )}
                        </Card>
                      </Col>
                    </Row>

                    <Card title="📋 Chi Tiết Trạng Thái" variant="borderless">
                      <Table
                        size="middle"
                        pagination={false}
                        dataSource={dashboardData.status_summary.map((s) => ({ ...s, key: s.status }))}
                        columns={[
                          {
                            title: 'Trạng Thái',
                            dataIndex: 'status',
                            key: 'status',
                            render: (status: string) => (
                              <Tag color={getStatusTagColor(status)}>{getStatusLabel(status)}</Tag>
                            ),
                          },
                          {
                            title: 'Số Đơn',
                            dataIndex: 'total_orders',
                            key: 'total_orders',
                            align: 'right',
                          },
                          {
                            title: 'Tổng Giá Trị',
                            dataIndex: 'total_value',
                            key: 'total_value',
                            align: 'right',
                            render: (value: number) => (
                              <Typography.Text strong style={{ color: '#1677ff' }}>
                                {formatCurrency(value)}
                              </Typography.Text>
                            ),
                          },
                        ]}
                      />
                    </Card>
                  </>
                ) : null}
              </Space>
            )}

        {/* Daily View */}
        {viewMode === 'daily' && (
          <>
            <Card variant="borderless" style={{ marginBottom: 16 }}>
              <Space wrap size={12}>
                <Typography.Text strong>Năm:</Typography.Text>
                <Select
                  value={selectedYear}
                  onChange={(value) => setSelectedYear(value)}
                  options={yearOptions}
                  style={{ width: 140 }}
                />
                <Typography.Text strong>Tháng:</Typography.Text>
                <Select
                  value={selectedMonth}
                  onChange={(value) => setSelectedMonth(value)}
                  options={monthOptions}
                  style={{ width: 160 }}
                />
              </Space>
            </Card>

            {isDailyLoading ? (
              <div className="text-center py-12">
                <Spin size="large" />
              </div>
            ) : dailyData ? (
              <>
                <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
                  <Col xs={24} md={12}>
                    <Card variant="borderless">
                      <Statistic
                        title="Tổng Doanh Thu"
                        value={formatCurrency(dailyData.total_revenue)}
                        styles={{ content: { color: '#1677ff', fontWeight: 700 } }}
                      />
                    </Card>
                  </Col>
                  <Col xs={24} md={12}>
                    <Card variant="borderless">
                      <Statistic
                        title="Tổng Đơn Hàng"
                        value={dailyData.total_orders}
                        styles={{ content: { color: '#22c55e', fontWeight: 700 } }}
                      />
                    </Card>
                  </Col>
                </Row>

                <Card
                  variant="borderless"
                  title={`Doanh Thu Theo Ngày - Tháng ${selectedMonth}/${selectedYear}`}
                >
                  {dailyChartData && (
                    <div className="h-96">
                      <Bar
                        data={dailyChartData}
                        options={{
                          maintainAspectRatio: false,
                          plugins: {
                            legend: { display: true, position: 'top' },
                            tooltip: {
                              callbacks: {
                                label: (context) => {
                                  const value = context.parsed.y ?? 0;
                                  return `Doanh thu: ${formatCurrency(value)}`;
                                },
                              },
                            },
                          },
                          scales: {
                            y: {
                              beginAtZero: true,
                              ticks: {
                                callback: (value) => {
                                  return (value as number).toLocaleString('vi-VN') + 'đ';
                                },
                              },
                            },
                          },
                        }}
                      />
                    </div>
                  )}
                </Card>
              </>
            ) : null}
          </>
        )}

        {/* Monthly View */}
        {viewMode === 'monthly' && (
          <>
            <Card variant="borderless" style={{ marginBottom: 16 }}>
              <Space wrap size={12}>
                <Typography.Text strong>Năm:</Typography.Text>
                <Select
                  value={selectedYear}
                  onChange={(value) => setSelectedYear(value)}
                  options={yearOptions.map((y) => ({ ...y, label: `Năm ${y.value}` }))}
                  style={{ width: 180 }}
                />
              </Space>
            </Card>

            {isMonthlyLoading ? (
              <div className="text-center py-12">
                <Spin size="large" />
              </div>
            ) : monthlyData ? (
              <>
                <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
                  <Col xs={24} md={12}>
                    <Card variant="borderless">
                      <Statistic
                        title="Tổng Doanh Thu Năm"
                        value={formatCurrency(monthlyData.total_revenue)}
                        styles={{ content: { color: '#22c55e', fontWeight: 700 } }}
                      />
                    </Card>
                  </Col>
                  <Col xs={24} md={12}>
                    <Card variant="borderless">
                      <Statistic
                        title="Tổng Đơn Hàng Năm"
                        value={monthlyData.total_orders}
                        styles={{ content: { color: '#a855f7', fontWeight: 700 } }}
                      />
                    </Card>
                  </Col>
                </Row>

                <Card variant="borderless" title={`Doanh Thu Theo Tháng - Năm ${selectedYear}`}>
                  {monthlyChartData && (
                    <div className="h-96">
                      <Line
                        data={monthlyChartData}
                        options={{
                          maintainAspectRatio: false,
                          plugins: {
                            legend: { display: true, position: 'top' },
                            tooltip: {
                              callbacks: {
                                label: (context) => {
                                  const value = context.parsed.y ?? 0;
                                  return `Doanh thu: ${formatCurrency(value)}`;
                                },
                              },
                            },
                          },
                          scales: {
                            y: {
                              beginAtZero: true,
                              ticks: {
                                callback: (value) => {
                                  return (value as number).toLocaleString('vi-VN') + 'đ';
                                },
                              },
                            },
                          },
                        }}
                      />
                    </div>
                  )}
                </Card>
              </>
            ) : null}
          </>
        )}
          </Card>
        </Space>
      </div>
    </div>
  );
}
