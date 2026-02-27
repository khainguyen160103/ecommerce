'use client';

import React, { useState } from 'react';
import {
  Empty,
  Pagination,
  Spin,
  Modal,
  Button,
  Tabs,
  Typography,
  Space,
  Breadcrumb,
} from 'antd';
import {
  ExclamationCircleOutlined,
  ShoppingOutlined,
  HomeOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { useOrder } from '@/hook/useOrder';
import OrderCard from '@/components/order/OrderCard';
import Link from 'next/link';

const { Title } = Typography;
const PAGE_SIZE = 10;

const ORDER_TABS = [
  { key: 'all', label: 'Tất cả' },
  { key: 'pending', label: 'Chờ xác nhận' },
  { key: 'confirmed', label: 'Đã xác nhận' },
  { key: 'shipping', label: 'Đang giao' },
  { key: 'delivered', label: 'Đã giao' },
  { key: 'cancelled', label: 'Đã hủy' },
];

export default function MyOrdersPage() {
  const [currentPage, setCurrentPage] = useState(1);
  const [activeTab, setActiveTab] = useState('all');
  const [cancellingId, setCancellingId] = useState<string | null>(null);
  const { useGetMyOrders, useCancelOrder } = useOrder();
  const { data: ordersData, isLoading, isFetching } = useGetMyOrders(
    (currentPage - 1) * PAGE_SIZE,
    PAGE_SIZE
  );
  const { mutate: cancelOrder } = useCancelOrder();

  const allOrders = Array.isArray(ordersData) ? ordersData : [];
  const orders =
    activeTab === 'all'
      ? allOrders
      : allOrders.filter((o: any) => o.status?.toLowerCase() === activeTab);
  const total = orders.length;

  const handleCancelOrder = (orderId: string) => {
    Modal.confirm({
      title: 'Hủy đơn hàng',
      icon: <ExclamationCircleOutlined />,
      content:
        'Bạn có chắc chắn muốn hủy đơn hàng này? Hành động này không thể hoàn tác.',
      okText: 'Hủy đơn',
      cancelText: 'Không',
      okButtonProps: { danger: true },
      onOk() {
        setCancellingId(orderId);
        cancelOrder(orderId, {
          onSettled: () => setCancellingId(null),
        });
      },
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto px-4 py-6">
        {/* Breadcrumb */}
        <Breadcrumb
          className="mb-4"
          items={[
            {
              href: '/',
              title: (
                <>
                  <HomeOutlined />
                  <span>Trang chủ</span>
                </>
              ),
            },
            {
              href: '/profile',
              title: (
                <>
                  <UserOutlined />
                  <span>Tài khoản</span>
                </>
              ),
            },
            { title: 'Đơn hàng' },
          ]}
        />

        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <Title level={3} style={{ margin: 0 }}>
            <ShoppingOutlined className="mr-2" />
            Đơn hàng của tôi
          </Title>
          <Link href="/profile">
            <Button>
              <UserOutlined />
              Tài khoản
            </Button>
          </Link>
        </div>

        {/* Tabs */}
        <Tabs
          activeKey={activeTab}
          onChange={(key) => {
            setActiveTab(key);
            setCurrentPage(1);
          }}
          items={ORDER_TABS.map((tab) => ({
            key: tab.key,
            label: tab.label,
          }))}
          style={{ marginBottom: 16 }}
        />

        {/* Content */}
        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '80px 0' }}>
            <Spin size="large" />
          </div>
        ) : orders.length === 0 ? (
          <div className="bg-white rounded-lg py-16">
            <Empty
              description={
                activeTab === 'all'
                  ? 'Bạn chưa có đơn hàng nào'
                  : `Không có đơn hàng "${ORDER_TABS.find((t) => t.key === activeTab)?.label}"`
              }
            >
              <Link href="/">
                <Button type="primary" size="large">
                  Tiếp tục mua sắm
                </Button>
              </Link>
            </Empty>
          </div>
        ) : (
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            {orders.map((order: any) => (
              <OrderCard
                key={order.id}
                order={order}
                isAdmin={false}
                onCancel={handleCancelOrder}
                loading={cancellingId === order.id}
              />
            ))}

            {total > PAGE_SIZE && (
              <div style={{ textAlign: 'center', marginTop: 20, marginBottom: 20 }}>
                <Pagination
                  current={currentPage}
                  pageSize={PAGE_SIZE}
                  total={total}
                  onChange={(page) => setCurrentPage(page)}
                  disabled={isFetching}
                  showTotal={(t) => `Tổng ${t} đơn hàng`}
                />
              </div>
            )}
          </Space>
        )}
      </div>
    </div>
  );
}
