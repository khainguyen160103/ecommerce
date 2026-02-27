'use client';

import React, { useState } from 'react';
import {
  Table,
  Row,
  Col,
  Select,
  Input,
  Button,
  Spin,
  Empty,
  Tooltip,
} from 'antd';
import { EyeOutlined, ReloadOutlined, UnorderedListOutlined } from '@ant-design/icons';
import Link from 'next/link';
import { useOrder } from '@/hook/useOrder';
import { OrderStatusBadge } from '@/components/order/OrderStatusBadge';
import { formatDate } from '@/utils/formatDate';

const ORDER_STATUSES = [
  { label: 'Tất cả', value: '' },
  { label: 'Chờ xác nhận', value: 'pending' },
  { label: 'Đã xác nhận', value: 'confirmed' },
  { label: 'Đang giao', value: 'shipping' },
  { label: 'Đã giao', value: 'delivered' },
  { label: 'Đã hủy', value: 'cancelled' },
];

export default function OrderPage() {
  const [pageIndex, setPageIndex] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [statusFilter, setStatusFilter] = useState('');
  const [searchText, setSearchText] = useState('');

  const { useGetAllOrders } = useOrder();
  const { data: ordersData, isLoading, isFetching, refetch } = useGetAllOrders(
    pageIndex * pageSize,
    pageSize,
    statusFilter
  );

  const orders = ordersData?.orders || [];
  const totalOrders = ordersData?.total || 0;

  const columns = [
    {
      title: 'Mã đơn hàng',
      dataIndex: 'id',
      key: 'id',
      render: (id: string) => (
        <Tooltip title={id}>
          <code>{id.substring(0, 8)}</code>
        </Tooltip>
      ),
      width: 100,
    },
    {
      title: 'Email khách hàng',
      dataIndex: 'user_email',
      key: 'user_email',
      render: (email: string) => email || 'N/A',
      width: 200,
    },
    {
      title: 'Tổng tiền',
      dataIndex: 'total',
      key: 'total',
      render: (total: number) =>
        new Intl.NumberFormat('vi-VN', {
          style: 'currency',
          currency: 'VND',
        }).format(Number(total)),
      width: 120,
    },
    {
      title: 'Trạng thái',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => <OrderStatusBadge status={status} />,
      width: 120,
    },
    {
      title: 'Ngày tạo',
      dataIndex: 'create_at',
      key: 'create_at',
      render: (date: string) => formatDate(date),
      width: 120,
    },
    {
      title: 'Hành động',
      key: 'action',
      render: (_, record: any) => (
        <Link href={`/admin/order/${record.id}`}>
          <Button type="primary" size="small" icon={<EyeOutlined />}>
            Chi tiết
          </Button>
        </Link>
      ),
      width: 100,
    },
  ];

  return (
    <div>
        <div style={{ padding: '24px' }}>
          <Row gutter={[16, 16]} align="middle" style={{ marginBottom: 16 }}>
            <Col xs={24} sm={12} style={{ textAlign: 'left' }}>
              <Button
                icon={<ReloadOutlined />}
                onClick={() => refetch()}
                loading={isFetching}
              >
                Làm mới
              </Button>
            </Col>
          </Row>

          {/* Filters */}
          <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
            <Col xs={24} sm={12}>
              <Input
                placeholder="Tìm mã đơn hàng, email..."
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                allowClear
              />
            </Col>
            <Col xs={24} sm={12}>
              <Select
                style={{ width: '100%' }}
                placeholder="Lọc theo trạng thái"
                options={ORDER_STATUSES}
                value={statusFilter}
                onChange={setStatusFilter}
              />
            </Col>
          </Row>

          {/* Table */}
          {isLoading ? (
            <div style={{ textAlign: 'center', padding: '50px' }}>
              <Spin size="large" />
            </div>
          ) : orders.length === 0 ? (
            <Empty description="Không có đơn hàng nào" />
          ) : (
            <Table
              columns={columns}
              dataSource={orders}
              rowKey={(record) => record.id}
              pagination={{
                pageSize,
                total: totalOrders,
                current: pageIndex + 1,
                showSizeChanger: true,
                showTotal: (total) => `Tổng ${total} đơn hàng`,
                onChange: (page) => setPageIndex(page - 1),
                onShowSizeChange: (_, size) => {
                  setPageSize(size);
                  setPageIndex(0);
                },
              }}
              loading={isFetching}
              scroll={{ x: 1200 }}
            />
          )}
        </div>
      </div>
  );
}
