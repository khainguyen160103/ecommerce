import React from 'react';
import { Tag } from 'antd';
import { CheckCircleOutlined, SyncOutlined, CarOutlined, ShoppingOutlined, CloseCircleOutlined } from '@ant-design/icons';

interface OrderStatusBadgeProps {
  status: string;
}

export const OrderStatusBadge: React.FC<OrderStatusBadgeProps> = ({ status }) => {
  const statusConfig: Record<string, { color: string; icon: React.ReactNode; label: string }> = {
    pending: { color: 'processing', icon: <ShoppingOutlined />, label: 'Chờ xác nhận' },
    confirmed: { color: 'warning', icon: <SyncOutlined />, label: 'Đã xác nhận' },
    shipping: { color: 'processing', icon: <CarOutlined />, label: 'Đang giao' },
    delivered: { color: 'success', icon: <CheckCircleOutlined />, label: 'Đã giao' },
    cancelled: { color: 'error', icon: <CloseCircleOutlined />, label: 'Đã hủy' },
  };

  const config = statusConfig[status.toLowerCase()] || statusConfig.pending;

  return (
    <Tag icon={config.icon} color={config.color}>
      {config.label}
    </Tag>
  );
};

export default OrderStatusBadge;
