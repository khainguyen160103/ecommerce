'use client';

import React, { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Card, Result, Button, Spin, Descriptions, Typography, Space, Divider } from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  ShoppingOutlined,
  FileTextOutlined,
  LoadingOutlined,
} from '@ant-design/icons';
import Link from 'next/link';
import { useCheckout } from '@/hook/useCheckout';

const { Text, Title } = Typography;

function CheckoutResultContent() {
  const searchParams = useSearchParams();
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const { useVerifyVNPay } = useCheckout();
  const { mutate: verifyVNPay } = useVerifyVNPay();

  useEffect(() => {
    const statusParam = searchParams.get('status');
    const orderIdParam = searchParams.get('order_id');
    const methodParam = searchParams.get('method');

    // Nếu là COD redirect
    if (statusParam === 'success' && methodParam === 'cod') {
      setResult({
        success: true,
        message: 'Đặt hàng thành công!',
        order_id: orderIdParam,
        method: 'cod',
      });
      setLoading(false);
      return;
    }

    // Nếu là VNPay return
    const vnpResponseCode = searchParams.get('vnp_ResponseCode');
    if (vnpResponseCode !== null) {
      const params = searchParams.toString();
      verifyVNPay(params, {
        onSuccess: (data) => {
          setResult({
            ...data,
            method: 'vnpay',
          });
          setLoading(false);
        },
        onError: () => {
          // Fallback: parse from URL params
          const isSuccess = vnpResponseCode === '00';
          setResult({
            success: isSuccess,
            message: isSuccess
              ? 'Thanh toán thành công!'
              : 'Thanh toán thất bại',
            order_id: searchParams.get('vnp_TxnRef'),
            amount: searchParams.get('vnp_Amount')
              ? parseInt(searchParams.get('vnp_Amount')!) / 100
              : null,
            transaction_no: searchParams.get('vnp_TransactionNo'),
            bank_code: searchParams.get('vnp_BankCode'),
            method: 'vnpay',
          });
          setLoading(false);
        },
      });
      return;
    }

    // Không có params hợp lệ
    setResult({
      success: false,
      message: 'Không tìm thấy thông tin thanh toán',
    });
    setLoading(false);
  }, [searchParams]); // eslint-disable-line react-hooks/exhaustive-deps

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-lg shadow-md text-center">
          <Spin indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />} />
          <Title level={4} className="mt-4">
            Đang xử lý kết quả thanh toán...
          </Title>
          <Text className="text-gray-500">Vui lòng không đóng trang này</Text>
        </Card>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Result
          status="warning"
          title="Không tìm thấy thông tin thanh toán"
          extra={
            <Link href="/">
              <Button type="primary">Về trang chủ</Button>
            </Link>
          }
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-2xl mx-auto px-4">
        <Card className="shadow-md">
          {result.success ? (
            <Result
              icon={
                <CheckCircleOutlined
                  style={{ color: '#52c41a', fontSize: 72 }}
                />
              }
              title={
                <Title level={3} style={{ color: '#52c41a' }}>
                  {result.message || 'Đặt hàng thành công!'}
                </Title>
              }
              subTitle={
                result.method === 'vnpay'
                  ? 'Thanh toán VNPay đã được xác nhận. Cảm ơn bạn đã mua hàng!'
                  : 'Đơn hàng của bạn đã được tạo. Bạn sẽ thanh toán khi nhận hàng.'
              }
            >
              <Divider />

              <Descriptions column={1} bordered size="small">
                {result.order_id && (
                  <Descriptions.Item label="Mã đơn hàng">
                    <Text copyable strong>
                      {result.order_id.substring(0, 8)}...
                    </Text>
                  </Descriptions.Item>
                )}
                <Descriptions.Item label="Phương thức">
                  {result.method === 'vnpay' ? (
                    <Space>
                      <Text>VNPay QR</Text>
                    </Space>
                  ) : (
                    <Text>Thanh toán khi nhận hàng (COD)</Text>
                  )}
                </Descriptions.Item>
                {result.amount && (
                  <Descriptions.Item label="Số tiền">
                    <Text strong className="text-orange-600">
                      {Number(result.amount).toLocaleString('vi-VN')}₫
                    </Text>
                  </Descriptions.Item>
                )}
                {result.transaction_no && (
                  <Descriptions.Item label="Mã giao dịch">
                    <Text copyable>{result.transaction_no}</Text>
                  </Descriptions.Item>
                )}
                {result.bank_code && (
                  <Descriptions.Item label="Ngân hàng">
                    {result.bank_code}
                  </Descriptions.Item>
                )}
              </Descriptions>

              <Divider />

              <Space className="w-full justify-center" size="middle">
                {result.order_id && (
                  <Link href={`/profile/order/${result.order_id}`}>
                    <Button type="primary" icon={<FileTextOutlined />} size="large">
                      Xem đơn hàng
                    </Button>
                  </Link>
                )}
                <Link href="/">
                  <Button icon={<ShoppingOutlined />} size="large">
                    Tiếp tục mua sắm
                  </Button>
                </Link>
              </Space>
            </Result>
          ) : (
            <Result
              icon={
                <CloseCircleOutlined
                  style={{ color: '#ff4d4f', fontSize: 72 }}
                />
              }
              title={
                <Title level={3} style={{ color: '#ff4d4f' }}>
                  {result.message || 'Thanh toán thất bại'}
                </Title>
              }
              subTitle="Đã có lỗi xảy ra trong quá trình thanh toán. Vui lòng thử lại."
            >
              {result.response_code && (
                <>
                  <Divider />
                  <Descriptions column={1} bordered size="small">
                    <Descriptions.Item label="Mã lỗi">
                      {result.response_code}
                    </Descriptions.Item>
                    {result.order_id && (
                      <Descriptions.Item label="Mã đơn hàng">
                        <Text copyable>{result.order_id}</Text>
                      </Descriptions.Item>
                    )}
                  </Descriptions>
                </>
              )}

              <Divider />

              <Space className="w-full justify-center" size="middle">
                <Link href="/profile/orders">
                  <Button type="primary" icon={<FileTextOutlined />} size="large">
                    Xem đơn hàng
                  </Button>
                </Link>
                <Link href="/">
                  <Button icon={<ShoppingOutlined />} size="large">
                    Về trang chủ
                  </Button>
                </Link>
              </Space>
            </Result>
          )}
        </Card>
      </div>
    </div>
  );
}

export default function CheckoutResultPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <Spin size="large" />
        </div>
      }
    >
      <CheckoutResultContent />
    </Suspense>
  );
}
