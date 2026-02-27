'use client';

import React from 'react';
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
  Modal,
  Steps,
  Typography,
  Space,
  Divider,
  Tag,
  Breadcrumb,
} from 'antd';
import {
  ArrowLeftOutlined,
  DeleteOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  SyncOutlined,
  CarOutlined,
  ShoppingOutlined,
  CloseCircleOutlined,
  HomeOutlined,
  UserOutlined,
} from '@ant-design/icons';
import Link from 'next/link';
import { useOrder } from '@/hook/useOrder';
import { OrderStatusBadge } from '@/components/order/OrderStatusBadge';
import { formatDate } from '@/utils/formatDate';

const { Title, Text } = Typography;

const STATUS_STEPS = ['pending', 'confirmed', 'shipping', 'delivered'];

function getStatusStep(status: string): number {
  if (status === 'cancelled') return -1;
  const idx = STATUS_STEPS.indexOf(status?.toLowerCase());
  return idx >= 0 ? idx : 0;
}

export default function OrderDetailPage() {
  const params = useParams();
  const orderId = params?.id as string;
  const { useGetMyOrderById, useCancelOrder } = useOrder();
  const { data: order, isLoading, error } = useGetMyOrderById(orderId);
  const { mutate: cancelOrder, isPending: isCancelling } = useCancelOrder();

  const handleCancel = () => {
    Modal.confirm({
      title: 'Hủy đơn hàng',
      icon: <ExclamationCircleOutlined />,
      content: 'Bạn có chắc chắn muốn hủy đơn hàng này?',
      okText: 'Hủy đơn',
      cancelText: 'Không',
      okButtonProps: { danger: true },
      onOk() {
        cancelOrder(orderId);
      },
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-5xl mx-auto px-4 py-6">
          <div style={{ textAlign: 'center', padding: '80px 0' }}>
            <Spin size="large" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-5xl mx-auto px-4 py-6">
          <div className="bg-white rounded-lg py-16">
            <Empty description="Không tìm thấy đơn hàng">
              <Link href="/profile/orders">
                <Button type="primary">Quay lại danh sách</Button>
              </Link>
            </Empty>
          </div>
        </div>
      </div>
    );
  }

  const isCancelled = order.status?.toLowerCase() === 'cancelled';
  const currentStep = getStatusStep(order.status);

  const columns = [
    {
      title: 'Sản phẩm',
      key: 'productName',
      render: (_: any, record: any) =>
        record.product_name ||
        record.product_detail?.product?.name ||
        record.product_detail?.name ||
        'N/A',
    },
    {
      title: 'Đơn giá',
      key: 'price',
      render: (_: any, record: any) => {
        const price =
          record.product_price ??
          record.product_detail?.price ??
          0;
        return new Intl.NumberFormat('vi-VN', {
          style: 'currency',
          currency: 'VND',
        }).format(Number(price));
      },
    },
    {
      title: 'Số lượng',
      dataIndex: 'quantity',
      key: 'quantity',
    },
    {
      title: 'Thành tiền',
      key: 'total',
      render: (_: any, record: any) => {
        const price =
          record.product_price ??
          record.product_detail?.price ??
          0;
        return (
          <Text strong className="text-orange-600">
            {new Intl.NumberFormat('vi-VN', {
              style: 'currency',
              currency: 'VND',
            }).format(Number(price) * record.quantity)}
          </Text>
        );
      },
    },
  ];

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
            {
              href: '/profile/orders',
              title: 'Đơn hàng',
            },
            { title: `#${order.id?.substring(0, 8)}` },
          ]}
        />

        {/* Back button + title */}
        <div className="flex items-center gap-3 mb-4">
          <Link href="/profile/orders">
            <Button icon={<ArrowLeftOutlined />}>Quay lại</Button>
          </Link>
          <Title level={4} style={{ margin: 0 }}>
            Đơn hàng #{order.id?.substring(0, 8)}
          </Title>
        </div>

        {/* Order progress */}
        {!isCancelled ? (
          <Card style={{ marginBottom: 16 }}>
            <Steps
              current={currentStep}
              size="small"
              items={[
                {
                  title: 'Chờ xác nhận',
                  icon: <ShoppingOutlined />,
                },
                {
                  title: 'Đã xác nhận',
                  icon: <SyncOutlined />,
                },
                {
                  title: 'Đang giao hàng',
                  icon: <CarOutlined />,
                },
                {
                  title: 'Đã giao',
                  icon: <CheckCircleOutlined />,
                },
              ]}
            />
          </Card>
        ) : (
          <Card style={{ marginBottom: 16 }}>
            <div className="text-center">
              <CloseCircleOutlined style={{ fontSize: 32, color: '#ff4d4f' }} />
              <Title level={5} style={{ color: '#ff4d4f', marginTop: 8 }}>
                Đơn hàng đã bị hủy
              </Title>
            </div>
          </Card>
        )}

        {/* Order info */}
        <Card title="Thông tin đơn hàng" style={{ marginBottom: 16 }}>
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12}>
              <Descriptions column={1} size="small">
                <Descriptions.Item label="Mã đơn hàng">
                  <Text copyable code>{order.id}</Text>
                </Descriptions.Item>
                <Descriptions.Item label="Ngày đặt">
                  {formatDate(order.create_at)}
                </Descriptions.Item>
                <Descriptions.Item label="Trạng thái">
                  <OrderStatusBadge status={order.status} />
                </Descriptions.Item>
              </Descriptions>
            </Col>
            <Col xs={24} sm={12}>
              <Descriptions column={1} size="small">
                <Descriptions.Item label="Tổng tiền">
                  <Text strong style={{ fontSize: 18, color: '#ff7a45' }}>
                    {new Intl.NumberFormat('vi-VN', {
                      style: 'currency',
                      currency: 'VND',
                    }).format(Number(order.total))}
                  </Text>
                </Descriptions.Item>
                <Descriptions.Item label="Cập nhật">
                  {formatDate(order.update_at)}
                </Descriptions.Item>
              </Descriptions>
            </Col>
          </Row>
        </Card>

        {/* Product list */}
        <Card title="Chi tiết sản phẩm" style={{ marginBottom: 16 }}>
          <Table
            columns={columns}
            dataSource={order.items || []}
            rowKey={(record: any, index) => record.id || `item-${index}`}
            pagination={false}
            scroll={{ x: 600 }}
            summary={() => (
              <Table.Summary.Row>
                <Table.Summary.Cell index={0} colSpan={3}>
                  <Text strong>Tổng cộng</Text>
                </Table.Summary.Cell>
                <Table.Summary.Cell index={1}>
                  <Text strong style={{ color: '#ff7a45', fontSize: 16 }}>
                    {new Intl.NumberFormat('vi-VN', {
                      style: 'currency',
                      currency: 'VND',
                    }).format(Number(order.total))}
                  </Text>
                </Table.Summary.Cell>
              </Table.Summary.Row>
            )}
          />
        </Card>

        {/* Cancel button */}
        {order.status?.toLowerCase() === 'pending' && (
          <Row justify="end">
            <Col>
              <Button
                danger
                size="large"
                icon={<DeleteOutlined />}
                onClick={handleCancel}
                loading={isCancelling}
              >
                Hủy đơn hàng
              </Button>
            </Col>
          </Row>
        )}
      </div>
    </div>
  );
}
