"use client";

import React, { useState, useEffect, useMemo } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Button,
  Input,
  Radio,
  Divider,
  Spin,
  Card,
  Typography,
  Space,
  Empty,
  Modal,
  Form,
  Breadcrumb,
  Tag,
  Select,
} from "antd";
import {
  HomeOutlined,
  ShoppingCartOutlined,
  EnvironmentOutlined,
  PlusOutlined,
  CreditCardOutlined,
  CarOutlined,
  LoadingOutlined,
} from "@ant-design/icons";
import { useCheckout } from "@/hook/useCheckout";
import { useAddress } from "@/hook/useAddress";
import { useGoShip } from "@/hook/useGoShip";
import toast from "react-hot-toast";

const { Title, Text } = Typography;
const { TextArea } = Input;

export default function CheckoutPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Đọc item_ids từ URL (truyền từ trang Cart)
  const itemIds = useMemo(() => {
    const ids = searchParams.get("item_ids");
    return ids ? ids.split(",").filter(Boolean) : undefined;
  }, [searchParams]);

  // ── Hooks ──
  const { useOrderPreview, useCreateCheckout, useShippingRates } = useCheckout();
  const { data: preview, isLoading: previewLoading } = useOrderPreview(itemIds);
  const { mutateAsync: createCheckout, isPending: isCreating } = useCreateCheckout();

  const { useGetMyAddresses, useCreateAddress } = useAddress();
  const { data: addressesData, isLoading: addressLoading } = useGetMyAddresses();
  const { mutateAsync: createAddress, isPending: isAddingAddress } = useCreateAddress();

  const { useGetCities, useGetDistricts, useGetWards } = useGoShip();

  // ── State ──
  const [selectedAddressId, setSelectedAddressId] = useState<string | null>(null);
  const [paymentMethod, setPaymentMethod] = useState<"cod" | "vnpay">("cod");
  const [selectedRateId, setSelectedRateId] = useState<string | null>(null);
  const [note, setNote] = useState("");
  const [showAddressModal, setShowAddressModal] = useState(false);
  const [addressForm] = Form.useForm();

  // GoShip location state cho modal thêm địa chỉ
  const [modalCityId, setModalCityId] = useState<number | undefined>();
  const [modalDistrictId, setModalDistrictId] = useState<number | undefined>();

  // GoShip location queries
  const { data: cities, isLoading: citiesLoading } = useGetCities();
  const { data: districts, isLoading: districtsLoading } = useGetDistricts(modalCityId);
  const { data: wards, isLoading: wardsLoading } = useGetWards(modalDistrictId);

  // ── Shipping rates (GoShip) ──
  const { data: shippingData, isLoading: shippingLoading } = useShippingRates(
    selectedAddressId || ""
  );

  const addresses = useMemo(
    () => (Array.isArray(addressesData) ? addressesData : []),
    [addressesData]
  );

  const shippingRates = useMemo(
    () => shippingData?.rates || [],
    [shippingData]
  );

  // Auto-select first address or from preview
  useEffect(() => {
    if (!selectedAddressId) {
      if (preview?.address?.id) {
        setSelectedAddressId(preview.address.id);
      } else if (addresses.length > 0) {
        setSelectedAddressId(addresses[0].id);
      }
    }
  }, [preview, addresses, selectedAddressId]);
  useEffect(() => {
    if (shippingRates.length > 0 && !shippingRates.find((r: any) => r.id === selectedRateId)) {
      setSelectedRateId(shippingRates[0].id);
    }
  }, [shippingRates, selectedRateId]);

  // ── Calculations ──
  const items = preview?.items || [];
  const subtotal = preview?.subtotal || 0;
  const selectedShipping = shippingRates.find((r: any) => r.id === selectedRateId);
  const shippingFee = selectedShipping?.fee || 0;
  const total = subtotal + shippingFee;

  // ── Handlers ──

  // Reset district/ward khi đổi city
  const handleCityChange = (cityId: number) => {
    setModalCityId(cityId);
    setModalDistrictId(undefined);
    addressForm.setFieldsValue({ district_id: undefined, ward_id: undefined });
  };

  // Reset ward khi đổi district
  const handleDistrictChange = (districtId: number) => {
    setModalDistrictId(districtId);
    addressForm.setFieldsValue({ ward_id: undefined });
  };

  const handleAddAddress = async () => {
    try {
      const values = await addressForm.validateFields();

      // Lấy tên từ danh sách GoShip
      const cityName = cities?.find((c: any) => c.id === values.city_id)?.name || "";
      const districtName = districts?.find((d: any) => d.id === values.district_id)?.name || "";
      const wardName = wards?.find((w: any) => w.id === values.ward_id)?.name || "";

      // Tạo địa chỉ đầy đủ
      const fullAddress = [values.street, wardName, districtName, cityName]
        .filter(Boolean)
        .join(", ");

      await createAddress({
        title: values.fullName || "Địa chỉ mới",
        address: fullAddress,
        phone_number: values.phone,
        city_id: values.city_id,
        district_id: values.district_id,
        ward_id: values.ward_id,
        city_name: cityName,
        district_name: districtName,
        ward_name: wardName,
      });

      addressForm.resetFields();
      setModalCityId(undefined);
      setModalDistrictId(undefined);
      setShowAddressModal(false);
    } catch {
      // validation error
    }
  };

  const handlePlaceOrder = async () => {
    if (!selectedAddressId && addresses.length === 0) {
      toast.error("Vui lòng thêm địa chỉ giao hàng");
      return;
    }

    if (!selectedRateId && shippingRates.length > 0) {
      toast.error("Vui lòng chọn phương thức vận chuyển");
      return;
    }

    try {
      const res = await createCheckout({
        payment_method: paymentMethod,
        address_id: selectedAddressId || undefined,
        shipping_method: selectedRateId || undefined,
        note,
        rate_id: selectedRateId || undefined,
        shipping_fee: shippingFee,
        item_ids: itemIds,
      });

      if (paymentMethod === "vnpay" && res.payment_url) {
        window.location.href = res.payment_url;
      } else {
        router.push(
          `/checkout/result?status=success&order_id=${res.order_id}&method=cod`
        );
      }
    } catch (error) {
      console.error("Checkout error:", error);
    }
  };

  // ── Loading state ──
  if (previewLoading || addressLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Spin size="large" />
      </div>
    );
  }

  // ── Empty cart ──
  if (!items || items.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Empty description="Giỏ hàng trống, không thể thanh toán">
          <Button type="primary" size="large" onClick={() => router.push("/")}>
            Tiếp tục mua sắm
          </Button>
        </Empty>
      </div>
    );
  }

  const selectedAddr = addresses.find((a: any) => a.id === selectedAddressId);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-6">
        {/* Breadcrumb */}
        <Breadcrumb
          className="mb-4"
          items={[
            { href: "/", title: <><HomeOutlined /> <span>Trang chủ</span></> },
            { href: "/cart", title: <><ShoppingCartOutlined /> <span>Giỏ hàng</span></> },
            { title: "Thanh toán" },
          ]}
        />

        <Title level={3} className="mb-6">
          <CreditCardOutlined className="mr-2" />
          Thanh toán
        </Title>

        <div className="flex flex-col lg:flex-row gap-6">
          {/* ===== LEFT COLUMN ===== */}
          <div className="flex-1 flex flex-col gap-6">
            {/* 1. Địa chỉ giao hàng */}
            <Card
              title={
                <Space>
                  <EnvironmentOutlined />
                  <span>Địa chỉ giao hàng</span>
                </Space>
              }
              extra={
                <Button
                  type="link"
                  icon={<PlusOutlined />}
                  onClick={() => setShowAddressModal(true)}
                >
                  Thêm mới
                </Button>
              }
            >
              {addresses.length === 0 ? (
                <div className="text-center py-6">
                  <Text className="text-gray-400">Bạn chưa có địa chỉ nào</Text>
                  <br />
                  <Button
                    type="primary"
                    className="mt-3"
                    icon={<PlusOutlined />}
                    onClick={() => setShowAddressModal(true)}
                  >
                    Thêm địa chỉ
                  </Button>
                </div>
              ) : (
                <Radio.Group
                  value={selectedAddressId}
                  onChange={(e) => {
                    setSelectedAddressId(e.target.value);
                    setSelectedRateId(null); // reset rate khi đổi địa chỉ
                  }}
                  className="w-full"
                >
                  <div className="flex flex-col gap-3">
                    {addresses.map((addr: any) => (
                      <Radio key={addr.id} value={addr.id} className="w-full">
                        <div className="ml-1">
                          <Text strong>{addr.title || "Địa chỉ"}</Text>
                          {addr.phone_number && (
                            <Text className="ml-2 text-gray-500">
                              | {addr.phone_number}
                            </Text>
                          )}
                          <br />
                          <Text className="text-gray-600 text-sm">
                            {addr.address}
                          </Text>
                        </div>
                      </Radio>
                    ))}
                  </div>
                </Radio.Group>
              )}
            </Card>

            {/* 2. Phương thức vận chuyển (GoShip) */}
            <Card
              title={
                <Space>
                  <CarOutlined />
                  <span>Phương thức vận chuyển</span>
                </Space>
              }
            >
              {!selectedAddressId ? (
                <Text className="text-gray-400">
                  Vui lòng chọn địa chỉ giao hàng để xem phí vận chuyển
                </Text>
              ) : shippingLoading ? (
                <div className="flex items-center gap-2 py-4 justify-center">
                  <LoadingOutlined />
                  <Text className="text-gray-500">Đang tính phí vận chuyển...</Text>
                </div>
              ) : shippingRates.length === 0 ? (
                <Text className="text-gray-400">
                  Không tìm thấy phương thức vận chuyển phù hợp
                </Text>
              ) : (
                <Radio.Group
                  value={selectedRateId}
                  onChange={(e) => setSelectedRateId(e.target.value)}
                  className="w-full"
                >
                  <div className="flex flex-col gap-3">
                    {shippingRates.map((rate: any) => (
                      <Radio key={rate.id} value={rate.id} className="w-full">
                        <div className="flex items-center justify-between w-full ml-1">
                          <div>
                            <Text strong>{rate.name}</Text>
                            {rate.carrier && (
                              <Text className="text-gray-400 text-xs ml-2">
                                ({rate.carrier})
                              </Text>
                            )}
                            <br />
                            <Text className="text-gray-500 text-xs">
                              {rate.estimated_days}
                            </Text>
                          </div>
                          <Tag
                            color={rate.fee === 0 ? "green" : "blue"}
                            className="ml-4"
                          >
                            {rate.fee === 0
                              ? "Miễn phí"
                              : `${rate.fee.toLocaleString("vi-VN")}đ`}
                          </Tag>
                        </div>
                      </Radio>
                    ))}
                  </div>
                </Radio.Group>
              )}
            </Card>

            {/* 3. Phương thức thanh toán */}
            <Card
              title={
                <Space>
                  <CreditCardOutlined />
                  <span>Phương thức thanh toán</span>
                </Space>
              }
            >
              <Radio.Group
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value)}
                className="w-full"
              >
                <div className="flex flex-col gap-3">
                  <Radio value="cod">
                    <div className="ml-1">
                      <Text strong>Thanh toán khi nhận hàng (COD)</Text>
                      <br />
                      <Text className="text-gray-500 text-xs">
                        Bạn sẽ thanh toán bằng tiền mặt khi nhận được hàng
                      </Text>
                    </div>
                  </Radio>
                  <Radio value="vnpay">
                    <div className="ml-1">
                      <Text strong>Thanh toán qua VNPay</Text>
                      <br />
                      <Text className="text-gray-500 text-xs">
                        Quét mã QR hoặc thanh toán qua ngân hàng trực tuyến
                      </Text>
                    </div>
                  </Radio>
                </div>
              </Radio.Group>
            </Card>

            {/* 4. Ghi chú */}
            <Card title="Ghi chú đơn hàng">
              <TextArea
                rows={3}
                placeholder="Ghi chú cho người bán (tùy chọn)..."
                value={note}
                onChange={(e) => setNote(e.target.value)}
                maxLength={500}
                showCount
              />
            </Card>
          </div>

          {/* ===== RIGHT COLUMN - Order Summary ===== */}
          <div className="w-full lg:w-[420px]">
            <div className="sticky top-20">
              <Card title={`Đơn hàng (${items.length} sản phẩm)`}>
                {/* Product list */}
                <div className="flex flex-col gap-4 max-h-[350px] overflow-y-auto pr-1">
                  {items.map((item: any, idx: number) => (
                    <div key={item.id || idx} className="flex gap-3">
                      <div className="flex-1 min-w-0">
                        <Text className="text-sm block truncate">
                          {item.product_name}
                        </Text>
                        <Text className="text-xs text-gray-400">
                          SL: {item.quantity}
                        </Text>
                      </div>
                      <Text className="text-sm font-medium whitespace-nowrap">
                        {(item.item_total || item.price * item.quantity).toLocaleString("vi-VN")}đ
                      </Text>
                    </div>
                  ))}
                </div>

                <Divider className="my-4" />

                {/* Address summary */}
                {selectedAddr && (
                  <>
                    <div className="mb-3">
                      <Text className="text-gray-500 text-xs block mb-1">
                        Giao đến:
                      </Text>
                      <Text strong className="text-sm">
                        {selectedAddr.title}
                      </Text>
                      {selectedAddr.phone_number && (
                        <Text className="text-sm"> - {selectedAddr.phone_number}</Text>
                      )}
                      <br />
                      <Text className="text-xs text-gray-500">
                        {selectedAddr.address}
                      </Text>
                    </div>
                    <Divider className="my-3" />
                  </>
                )}

                {/* Shipping summary */}
                {selectedShipping && (
                  <>
                    <div className="mb-3">
                      <Text className="text-gray-500 text-xs block mb-1">
                        Vận chuyển:
                      </Text>
                      <Text className="text-sm">
                        {selectedShipping.name}
                        {selectedShipping.carrier && ` (${selectedShipping.carrier})`}
                      </Text>
                      <br />
                      <Text className="text-xs text-gray-500">
                        {selectedShipping.estimated_days}
                      </Text>
                    </div>
                    <Divider className="my-3" />
                  </>
                )}

                {/* Totals */}
                <div className="flex flex-col gap-2 text-sm">
                  <div className="flex justify-between">
                    <Text className="text-gray-500">Tạm tính</Text>
                    <Text>{subtotal.toLocaleString("vi-VN")}đ</Text>
                  </div>
                  <div className="flex justify-between">
                    <Text className="text-gray-500">Phí vận chuyển</Text>
                    <Text>
                      {shippingFee > 0
                        ? `${shippingFee.toLocaleString("vi-VN")}đ`
                        : "Miễn phí"}
                    </Text>
                  </div>
                </div>

                <Divider className="my-3" />

                <div className="flex justify-between items-center">
                  <Text strong className="text-base">
                    Tổng cộng
                  </Text>
                  <Text strong className="text-xl text-red-500">
                    {total.toLocaleString("vi-VN")}đ
                  </Text>
                </div>

                <Button
                  type="primary"
                  size="large"
                  block
                  className="mt-5"
                  onClick={handlePlaceOrder}
                  loading={isCreating}
                  disabled={items.length === 0}
                >
                  {paymentMethod === "vnpay"
                    ? "Thanh toán qua VNPay"
                    : "Đặt hàng"}
                </Button>

                <div className="mt-3 text-center">
                  <Text className="text-xs text-gray-400">
                    Bằng việc đặt hàng, bạn đồng ý với điều khoản sử dụng
                  </Text>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </div>

      {/* ===== Add Address Modal (GoShip cascading selectors) ===== */}
      <Modal
        title="Thêm địa chỉ mới"
        open={showAddressModal}
        onCancel={() => {
          setShowAddressModal(false);
          addressForm.resetFields();
          setModalCityId(undefined);
          setModalDistrictId(undefined);
        }}
        onOk={handleAddAddress}
        okText="Thêm địa chỉ"
        cancelText="Bỏ qua"
        confirmLoading={isAddingAddress}
        width={560}
      >
        <Form form={addressForm} layout="vertical" className="mt-4">
          <Form.Item
            name="fullName"
            label="Họ và tên"
            rules={[{ required: true, message: "Vui lòng nhập họ tên" }]}
          >
            <Input placeholder="Nhập họ và tên người nhận" />
          </Form.Item>

          <Form.Item
            name="phone"
            label="Số điện thoại"
            rules={[{ required: true, message: "Vui lòng nhập số điện thoại" }]}
          >
            <Input placeholder="Nhập số điện thoại" />
          </Form.Item>

          <div className="grid grid-cols-3 gap-3">
            <Form.Item
              name="city_id"
              label="Tỉnh/Thành phố"
              rules={[{ required: true, message: "Chọn tỉnh/TP" }]}
            >
              <Select
                showSearch
                placeholder="Chọn tỉnh/TP"
                loading={citiesLoading}
                onChange={handleCityChange}
                optionFilterProp="label"
                options={(cities || []).map((c: any) => ({
                  value: c.id,
                  label: c.name,
                }))}
              />
            </Form.Item>

            <Form.Item
              name="district_id"
              label="Quận/Huyện"
              rules={[{ required: true, message: "Chọn quận/huyện" }]}
            >
              <Select
                showSearch
                placeholder="Chọn quận/huyện"
                loading={districtsLoading}
                disabled={!modalCityId}
                onChange={handleDistrictChange}
                optionFilterProp="label"
                options={(districts || []).map((d: any) => ({
                  value: d.id,
                  label: d.name,
                }))}
              />
            </Form.Item>

            <Form.Item
              name="ward_id"
              label="Phường/Xã"
              rules={[{ required: true, message: "Chọn phường/xã" }]}
            >
              <Select
                showSearch
                placeholder="Chọn phường/xã"
                loading={wardsLoading}
                disabled={!modalDistrictId}
                optionFilterProp="label"
                options={(wards || []).map((w: any) => ({
                  value: w.id,
                  label: w.name,
                }))}
              />
            </Form.Item>
          </div>

          <Form.Item
            name="street"
            label="Địa chỉ cụ thể"
            rules={[{ required: true, message: "Vui lòng nhập địa chỉ" }]}
          >
            <Input placeholder="Số nhà, tên đường..." />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}