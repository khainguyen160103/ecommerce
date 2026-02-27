'use client';

import React, { useState } from 'react';
import { useParams } from 'next/navigation';
import {
  Card,
  Row,
  Col,
  Table,
  Spin,
  Button,
  Descriptions,
  Empty,
  Select,
  Modal,
  message,
} from 'antd';
import {
  ArrowLeftOutlined,
  SaveOutlined,
  ExclamationCircleOutlined,
  UserOutlined,
} from '@ant-design/icons';
import Link from 'next/link';
import { useOrder } from '@/hook/useOrder';
import { OrderStatusBadge } from '@/components/order/OrderStatusBadge';
import { formatDate } from '@/utils/formatDate';

const ORDER_STATUS_OPTIONS = [
  { label: 'Chờ xác nhận', value: 'pending' },
  { label: 'Đã xác nhận', value: 'confirmed' },
  { label: 'Đang giao', value: 'shipping' },
  { label: 'Đã giao', value: 'delivered' },
  { label: 'Đã hủy', value: 'cancelled' },
];

export default function AdminOrderDetailPage() {
  const params = useParams();
  const orderId = params?.id as string;
  const [newStatus, setNewStatus] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  const { useGetOrderByIdAdmin, useUpdateOrderStatus } = useOrder();
  const { data: order, isLoading, error } = useGetOrderByIdAdmin(orderId);
  const { mutate: updateStatus } = useUpdateOrderStatus();

  const handleUpdateStatus = () => {
    if (!newStatus) {
      message.warning('Vui lòng chọn trạng thái');
      return;
    }

    Modal.confirm({
      title: 'Cập nhật trạng thái',
      icon: <ExclamationCircleOutlined />,
      content: `Bạn muốn cập nhật trạng thái thành "${
        ORDER_STATUS_OPTIONS.find((s) => s.value === newStatus)?.label
      }"?`,
      okText: 'Cập nhật',
      cancelText: 'Hủy',
      onOk() {
        setIsSaving(true);
        updateStatus(
          { orderId, status: newStatus },
          {
            onSettled: () => setIsSaving(false),
            onSuccess: () => {
              setNewStatus('');
            },
          }
        );
      },
    });
  };

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (error || !order) {
    return (
      <div style={{ padding: '24px' }}>
        <Empty description="Không tìm thấy đơn hàng" />
      </div>
    );
  }

  const columns = [
    {
      title: 'Sản phẩm',
      dataIndex: 'product_name',
      key: 'productName',
    },
    {
      title: 'Giá',
      dataIndex: 'product_price',
      key: 'price',
      render: (price: number) =>
        new Intl.NumberFormat('vi-VN', {
          style: 'currency',
          currency: 'VND',
        }).format(price),
    },
    {
      title: 'Số lượng',
      dataIndex: 'quantity',
      key: 'quantity',
    },
    {
      title: 'Tổng',
      key: 'total',
      render: (_, record: any) =>
        new Intl.NumberFormat('vi-VN', {
          style: 'currency',
          currency: 'VND',
        }).format((record.product_price || 0) * record.quantity),
    },
  ];

  return (
    <div>
      {/* Header */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24}>
              <Link href="/admin/order">
                <Button icon={<ArrowLeftOutlined />}>Quay lại</Button>
              </Link>
            </Col>
          </Row>

          {/* Order Info */}
          <Card title={`Chi tiết đơn hàng #${order.id?.substring(0, 8)}`} style={{ marginBottom: 16 }}>
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12}>
                <Descriptions column={1}>
                  <Descriptions.Item label="Mã đơn hàng">
                    <code>{order.id}</code>
                  </Descriptions.Item>
                  <Descriptions.Item label="Ngày tạo">
                    {formatDate(order.create_at)}
                  </Descriptions.Item>
                  <Descriptions.Item label="Cập nhật lần cuối">
                    {formatDate(order.update_at)}
                  </Descriptions.Item>
                </Descriptions>
              </Col>
              <Col xs={24} sm={12}>
                <Descriptions column={1}>
                  <Descriptions.Item label="Tổng tiền">
                    <span style={{ fontSize: 16, fontWeight: 'bold', color: '#ff7a45' }}>
                      {new Intl.NumberFormat('vi-VN', {
                        style: 'currency',
                        currency: 'VND',
                      }).format(Number(order.total))}
                    </span>
                  </Descriptions.Item>
                  <Descriptions.Item label="Trạng thái">
                    <OrderStatusBadge status={order.status} />
                  </Descriptions.Item>
                </Descriptions>
              </Col>
            </Row>
          </Card>

          {/* Customer Info */}
          <Card title={<><UserOutlined /> Thông tin khách hàng</>} style={{ marginBottom: 16 }}>
            <Descriptions column={1}>
              <Descriptions.Item label="Tên khách hàng">
                {order.user?.username || 'N/A'}
              </Descriptions.Item>
              <Descriptions.Item label="Email">
                {order.user?.email || 'N/A'}
              </Descriptions.Item>
              <Descriptions.Item label="Vai trò">
                <span style={{ textTransform: 'capitalize' }}>{order.user?.role || 'N/A'}</span>
              </Descriptions.Item>
            </Descriptions>
          </Card>

          {/* Order Items */}
          <Card title="Chi tiết sản phẩm" style={{ marginBottom: 16 }}>
            <Table
              columns={columns}
              dataSource={order.items || []}
              rowKey={(record, index) => `item-${index}`}
              pagination={false}
              scroll={{ x: 800 }}
            />
          </Card>

          {/* Status Update */}
          <Card title="Cập nhật trạng thái đơn hàng">
            <Row gutter={[16, 16]} align="middle">
              <Col xs={24} sm={16}>
                <Select
                  style={{ width: '100%' }}
                  placeholder="Chọn trạng thái mới"
                  options={ORDER_STATUS_OPTIONS}
                  value={newStatus}
                  onChange={setNewStatus}
                />
              </Col>
              <Col xs={24} sm={8}>
                <Button
                  type="primary"
                  block
                  icon={<SaveOutlined />}
                  onClick={handleUpdateStatus}
                  loading={isSaving}
                >
                  Cập nhật
                </Button>
              </Col>
            </Row>
          </Card>
        </div>
  );
}
