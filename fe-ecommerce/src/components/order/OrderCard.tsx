import React from 'react';
import { Card, Row, Col, Button, Space, Divider, Typography } from 'antd';
import { EyeOutlined, DeleteOutlined } from '@ant-design/icons';
import Link from 'next/link';
import { Order } from '@/models/order';
import { OrderStatusBadge } from './OrderStatusBadge';
import { formatDate } from '@/utils/formatDate';

interface OrderCardProps {
  order: Order;
  isAdmin?: boolean;
  onCancel?: (orderId: string) => void;
  loading?: boolean;
}

export const OrderCard: React.FC<OrderCardProps> = ({ order, isAdmin = false, onCancel, loading = false }) => {
  const viewPath = isAdmin ? `/admin/order/${order.id}` : `/profile/order/${order.id}`;
  console.log(order);

  return (
    <Card
      className="order-card"
      style={{ marginBottom: 16, borderRadius: 8 }}
      hoverable
    >
      <Row gutter={[16, 16]} align="middle">
        <Col xs={24} sm={12}>
          <Space direction="vertical" style={{ width: '100%' }} size="small">
            <div>
              <Typography.Text strong>Mã đơn:</Typography.Text>
              <Typography.Text copyable code style={{ marginLeft: 8 }}>
                {order.id}
              </Typography.Text>
            </div>
            <div>
              <Typography.Text strong>Ngày tạo:</Typography.Text>
              <Typography.Text style={{ marginLeft: 8 }}>
                {formatDate(order.create_at)}
              </Typography.Text>
            </div>
            <div>
              <Typography.Text strong>Sản phẩm:</Typography.Text>
              <Typography.Text style={{ marginLeft: 8 }}>
                {order.items_count} item
              </Typography.Text>
            </div>
          </Space>
        </Col>

        <Col xs={24} sm={12}>
          <Row gutter={[16, 16]} align="middle" justify="space-between">
            <Col xs={24} sm={12}>
              <div>
                <Typography.Text strong>Trạng thái:</Typography.Text>
                <div style={{ marginTop: 8 }}>
                  <OrderStatusBadge status={order.status} />
                </div>
              </div>
            </Col>
            <Col xs={24} sm={12}>
              <div>
                <Typography.Text strong>Tổng tiền:</Typography.Text>
                <Typography.Title
                  level={4}
                  style={{ color: '#ff7a45', marginBottom: 0, marginTop: 4 }}
                >
                  {new Intl.NumberFormat('vi-VN', {
                    style: 'currency',
                    currency: 'VND',
                  }).format(Number(order.total))}
                </Typography.Title>
              </div>
            </Col>
          </Row>
        </Col>
      </Row>

      <Divider style={{ margin: '12px 0' }} />

      <Row gutter={[8, 8]} justify="end">
        <Col>
          <Link href={viewPath}>
            <Button type="primary" icon={<EyeOutlined />}>
              Chi tiết
            </Button>
          </Link>
        </Col>
        {!isAdmin && order.status?.toLowerCase() === 'pending' && (
          <Col>
            <Button
              danger
              icon={<DeleteOutlined />}
              onClick={() => onCancel?.(order.id)}
              loading={loading}
            >
              Hủy đơn
            </Button>
          </Col>
        )}
      </Row>
    </Card>
  );
};

export default OrderCard;
