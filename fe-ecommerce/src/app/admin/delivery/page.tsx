'use client';

import React, { useState } from 'react';
import {
  Table,
  Row,
  Col,
  Select,
  Button,
  Spin,
  Empty,
  Tooltip,
  Tag,
  Modal,
  Descriptions,
  Timeline,
  Space,
} from 'antd';
import {
  ReloadOutlined,
  CarOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  SendOutlined,
  EyeOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons';
import Link from 'next/link';
import { useOrder } from '@/hook/useOrder';
import { useGoShip } from '@/hook/useGoShip';
import { OrderStatusBadge } from '@/components/order/OrderStatusBadge';
import { formatDate } from '@/utils/formatDate';

const DELIVERY_STATUSES = [
  { label: 'Tất cả giao hàng', value: '' },
  { label: 'Đã xác nhận (chờ giao)', value: 'confirmed' },
  { label: 'Đang giao hàng', value: 'shipping' },
  { label: 'Đã giao thành công', value: 'delivered' },
];

export default function DeliveryPage() {
  const [pageIndex, setPageIndex] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [statusFilter, setStatusFilter] = useState('confirmed');
  const [trackingOrderId, setTrackingOrderId] = useState<string | undefined>(undefined);

  const { useGetAllOrders, useUpdateOrderStatus } = useOrder();
  const { useCreateShipment, useGetTracking, useCancelShipment } = useGoShip();

  const { data: ordersData, isLoading, isFetching, refetch } = useGetAllOrders(
    pageIndex * pageSize,
    pageSize,
    statusFilter || undefined
  );
  const { mutate: updateStatus } = useUpdateOrderStatus();
  const { mutate: createShipment, isPending: isCreatingShipment } = useCreateShipment();
  const { data: trackingData, isLoading: isTrackingLoading } = useGetTracking(trackingOrderId);
  const { mutate: cancelShipment, isPending: isCancelling } = useCancelShipment();

  const orders = ordersData?.orders || [];
  const totalOrders = ordersData?.total || 0;

  const handleStatusUpdate = (orderId: string, newStatus: string, label: string) => {
    Modal.confirm({
      title: 'Xác nhận cập nhật',
      icon: <ExclamationCircleOutlined />,
      content: `Bạn muốn cập nhật trạng thái đơn hàng thành "${label}"?`,
      okText: 'Xác nhận',
      cancelText: 'Hủy',
      onOk() {
        updateStatus(
          { orderId, status: newStatus },
          {
            onSuccess: () => {
              refetch();
            },
          }
        );
      },
    });
  };

  const handleCreateShipment = (record: any) => {
    if (!record.rate_id) {
      Modal.warning({
        title: 'Không thể tạo đơn vận chuyển',
        content: 'Đơn hàng này chưa có thông tin phí vận chuyển (rate_id). Khách hàng cần chọn phương thức vận chuyển khi thanh toán.',
      });
      return;
    }
    Modal.confirm({
      title: 'Tạo đơn vận chuyển GoShip',
      icon: <SendOutlined />,
      content: (
        <div>
          <p>Bạn muốn tạo đơn vận chuyển GoShip cho đơn hàng này?</p>
          {record.carrier && <p>Đơn vị: <strong>{record.carrier}</strong></p>}
          {record.shipping_fee > 0 && (
            <p>Phí ship: <strong>{new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(record.shipping_fee)}</strong></p>
          )}
        </div>
      ),
      okText: 'Tạo đơn',
      cancelText: 'Hủy',
      onOk() {
        createShipment(
          { order_id: record.id, rate_id: record.rate_id },
          {
            onSuccess: (data: any) => {
              if (data?.fallback) {
                Modal.info({
                  title: 'Đã tạo vận đơn nội bộ',
                  content: (
                    <div>
                      <p>GoShip sandbox hiện không khả dụng.</p>
                      <p>Đã tạo mã vận đơn nội bộ: <strong>{data.shipping_code}</strong></p>
                      <p>Bạn có thể cập nhật trạng thái giao hàng thủ công.</p>
                    </div>
                  ),
                });
              }
              refetch();
            },
          }
        );
      },
    });
  };

  const handleCancelShipment = (orderId: string) => {
    Modal.confirm({
      title: 'Hủy đơn vận chuyển',
      icon: <CloseCircleOutlined style={{ color: '#ff4d4f' }} />,
      content: 'Bạn chắc chắn muốn hủy đơn vận chuyển GoShip này?',
      okText: 'Xác nhận hủy',
      cancelText: 'Không',
      okButtonProps: { danger: true },
      onOk() {
        cancelShipment(orderId, {
          onSuccess: () => {
            refetch();
          },
        });
      },
    });
  };

  const columns = [
    {
      title: 'Mã đơn hàng',
      dataIndex: 'id',
      key: 'id',
      render: (id: string) => (
        <Tooltip title={id}>
          <Link href={`/admin/order/${id}`}>
            <code style={{ cursor: 'pointer', color: '#1890ff' }}>{id.substring(0, 8)}...</code>
          </Link>
        </Tooltip>
      ),
      width: 120,
    },
    {
      title: 'Email khách hàng',
      dataIndex: 'user_email',
      key: 'user_email',
      render: (email: string) => email || 'N/A',
      width: 180,
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
      width: 130,
    },
    {
      title: 'Phí ship',
      dataIndex: 'shipping_fee',
      key: 'shipping_fee',
      render: (fee: number) =>
        fee > 0
          ? new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(fee)
          : <Tag>Chưa có</Tag>,
      width: 110,
    },
    {
      title: 'Đơn vị VC',
      dataIndex: 'carrier',
      key: 'carrier',
      render: (carrier: string, record: any) =>
        record.shipping_code ? (
          <Tooltip title={`Mã vận đơn: ${record.shipping_code}`}>
            <Tag color="blue">{carrier || 'GoShip'}</Tag>
          </Tooltip>
        ) : (
          <Tag color="default">Chưa tạo</Tag>
        ),
      width: 120,
    },
    {
      title: 'Trạng thái',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => <OrderStatusBadge status={status} />,
      width: 140,
    },
    {
      title: 'Ngày tạo',
      dataIndex: 'create_at',
      key: 'create_at',
      render: (date: string) => formatDate(date),
      width: 130,
    },
    {
      title: 'Thao tác',
      key: 'action',
      width: 280,
      fixed: 'right' as const,
      render: (_: any, record: any) => {
        const status = record.status;
        const hasShipment = !!record.shipping_code;
        return (
          <Space size={4} wrap>
            {/* Tạo đơn GoShip cho đơn confirmed chưa có shipping_code */}
            {status === 'confirmed' && !hasShipment && (
              <Button
                type="primary"
                size="small"
                icon={<SendOutlined />}
                loading={isCreatingShipment}
                onClick={() => handleCreateShipment(record)}
              >
                Tạo vận đơn
              </Button>
            )}

            {/* Cập nhật trạng thái giao hàng (thủ công nếu không dùng GoShip hoặc đã có shipment) */}
            {status === 'confirmed' && hasShipment && (
              <Button
                type="primary"
                size="small"
                icon={<CarOutlined />}
                onClick={() => handleStatusUpdate(record.id, 'shipping', 'Đang giao hàng')}
              >
                Giao hàng
              </Button>
            )}

            {status === 'shipping' && (
              <Button
                type="primary"
                size="small"
                style={{ backgroundColor: '#52c41a', borderColor: '#52c41a' }}
                icon={<CheckCircleOutlined />}
                onClick={() => handleStatusUpdate(record.id, 'delivered', 'Đã giao thành công')}
              >
                Đã giao
              </Button>
            )}

            {status === 'delivered' && (
              <Tag color="success" icon={<CheckCircleOutlined />}>
                Hoàn thành
              </Tag>
            )}

            {/* Tracking đơn đã có shipping_code */}
            {hasShipment && (
              <Button
                size="small"
                icon={<EyeOutlined />}
                onClick={() => setTrackingOrderId(record.id)}
              >
                Tracking
              </Button>
            )}

            {/* Hủy vận đơn (chỉ khi có shipping_code và chưa giao xong) */}
            {hasShipment && status !== 'delivered' && (
              <Button
                size="small"
                danger
                icon={<CloseCircleOutlined />}
                loading={isCancelling}
                onClick={() => handleCancelShipment(record.id)}
              >
                Hủy VC
              </Button>
            )}

            <Link href={`/admin/order/${record.id}`}>
              <Button size="small">Chi tiết</Button>
            </Link>
          </Space>
        );
      },
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={[16, 16]} align="middle" style={{ marginBottom: 16 }}>
        <Col flex="auto">
          <h2 style={{ margin: 0 }}>
            <CarOutlined style={{ marginRight: 8 }} />
            Quản lý giao hàng
          </h2>
        </Col>
        <Col>
          <Button
            icon={<ReloadOutlined />}
            onClick={() => refetch()}
            loading={isFetching}
          >
            Làm mới
          </Button>
        </Col>
      </Row>

      {/* Filter */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={8}>
          <Select
            style={{ width: '100%' }}
            placeholder="Lọc theo trạng thái giao hàng"
            options={DELIVERY_STATUSES}
            value={statusFilter}
            onChange={(val) => {
              setStatusFilter(val);
              setPageIndex(0);
            }}
          />
        </Col>
      </Row>

      {/* Summary */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col>
          <Tag color="blue" style={{ padding: '4px 12px', fontSize: 14 }}>
            Tổng: {totalOrders} đơn hàng
          </Tag>
        </Col>
      </Row>

      {/* Table */}
      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Spin size="large" />
        </div>
      ) : orders.length === 0 ? (
        <Empty description="Không có đơn hàng giao hàng nào" />
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

      {/* Tracking Modal */}
      <Modal
        title={
          <span>
            <EyeOutlined style={{ marginRight: 8 }} />
            Theo dõi vận chuyển
          </span>
        }
        open={!!trackingOrderId}
        onCancel={() => setTrackingOrderId(undefined)}
        footer={[
          <Button key="close" onClick={() => setTrackingOrderId(undefined)}>
            Đóng
          </Button>,
        ]}
        width={600}
      >
        {isTrackingLoading ? (
          <div style={{ textAlign: 'center', padding: 32 }}>
            <Spin size="large" />
          </div>
        ) : trackingData ? (
          <div>
            <Descriptions bordered column={1} size="small" style={{ marginBottom: 16 }}>
              <Descriptions.Item label="Mã vận đơn">
                {trackingData.shipping_code || 'N/A'}
              </Descriptions.Item>
              <Descriptions.Item label="Tracking Number">
                {trackingData.tracking_number || 'N/A'}
              </Descriptions.Item>
              <Descriptions.Item label="Đơn vị vận chuyển">
                {trackingData.carrier || 'N/A'}
              </Descriptions.Item>
              <Descriptions.Item label="Trạng thái">
                <Tag color="processing">{trackingData.status}</Tag>
              </Descriptions.Item>
            </Descriptions>

            {trackingData.tracking && Array.isArray(trackingData.tracking) && trackingData.tracking.length > 0 ? (
              <div>
                <h4>Lịch sử vận chuyển:</h4>
                <Timeline
                  items={trackingData.tracking.map((item: any, idx: number) => ({
                    key: idx,
                    children: (
                      <div>
                        <strong>{item.status || item.action}</strong>
                        {item.time && <div style={{ color: '#999', fontSize: 12 }}>{item.time}</div>}
                        {item.location && <div style={{ color: '#666', fontSize: 12 }}>{item.location}</div>}
                      </div>
                    ),
                  }))}
                />
              </div>
            ) : (
              <Empty description="Chưa có lịch sử vận chuyển" image={Empty.PRESENTED_IMAGE_SIMPLE} />
            )}
          </div>
        ) : (
          <Empty description="Không tìm thấy thông tin tracking" />
        )}
      </Modal>
    </div>
  );
}
