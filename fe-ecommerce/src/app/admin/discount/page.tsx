'use client'
import React, { useState } from 'react'
import {
  Button,
  Space,
  Table,
  Popconfirm,
  Form,
  Input,
  InputNumber,
  Modal,
  Tag,
  Select,
  DatePicker,
  Switch,
} from 'antd'
import { useDiscount } from '@/hook/useDiscount'
import Spinner from '@/components/Spinner'
import { formatDate } from '@/utils/formatDate'
import type { Discount } from '@/models/discount'
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'

dayjs.extend(utc)
dayjs.extend(timezone)

const VN_TZ = 'Asia/Ho_Chi_Minh'

const { Column } = Table

export default function DiscountPage() {
  const { discountsData, deleteMutation, updateMutation, createMutation } = useDiscount()
  const [isModalVisible, setIsModalVisible] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [form] = Form.useForm()

  const tableData: Discount[] = discountsData.data?.data || []

  const handleAdd = () => {
    setEditingId(null)
    form.resetFields()
    form.setFieldsValue({
      discount_type: 'percent',
      discount_value: 10,
      min_order_value: 0,
      is_active: true,
    })
    setIsModalVisible(true)
  }

  const handleEdit = (record: Discount) => {
    setEditingId(record.id)
    form.setFieldsValue({
      code: record.code,
      description: record.description,
      discount_type: record.discount_type,
      discount_value: record.discount_value,
      min_order_value: record.min_order_value,
      max_discount: record.max_discount,
      usage_limit: record.usage_limit,
      is_active: record.is_active,
      start_date: record.start_date ? dayjs(record.start_date).tz(VN_TZ) : null,
      end_date: record.end_date ? dayjs(record.end_date).tz(VN_TZ) : null,
    })
    setIsModalVisible(true)
  }

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields()

      // Format dates as Vietnam timezone string (YYYY-MM-DDTHH:mm:ss)
      // so the backend receives exact time the user selected
      const formatDateVN = (d: any) => {
        if (!d) return null
        return dayjs(d).tz(VN_TZ).format('YYYY-MM-DDTHH:mm:ss')
      }

      if (editingId) {
        // Only send fields that were actually changed
        const payload: Record<string, any> = {}
        const fields = ['code', 'description', 'discount_type', 'discount_value', 'min_order_value', 'max_discount', 'usage_limit', 'is_active', 'start_date', 'end_date']
        for (const field of fields) {
          if (values[field] !== undefined) {
            if (field === 'code') {
              payload[field] = values[field]?.toUpperCase()
            } else if (field === 'start_date' || field === 'end_date') {
              payload[field] = formatDateVN(values[field])
            } else {
              payload[field] = values[field]
            }
          }
        }
        await updateMutation.mutateAsync({ id: editingId, data: payload })
      } else {
        const payload = {
          ...values,
          code: values.code?.toUpperCase(),
          start_date: formatDateVN(values.start_date),
          end_date: formatDateVN(values.end_date),
        }
        await createMutation.mutateAsync(payload)
      }

      setIsModalVisible(false)
      form.resetFields()
    } catch (error) {
      console.log('Validate Failed:', error)
    }
  }

  const handleDelete = (id: string) => {
    deleteMutation.mutate(id)
  }

  const discountType = Form.useWatch('discount_type', form)

  return (
    <>
      {discountsData.isLoading ? (
        <Spinner />
      ) : (
        <>
          <Button
            className="w-fit"
            type="primary"
            style={{ marginBottom: 16 }}
            onClick={handleAdd}
          >
            Thêm Mã Giảm Giá
          </Button>

          <Table<Discount> dataSource={tableData} rowKey="id" scroll={{ x: 1400, y: 500 }}>
            <Column
              title="Mã"
              dataIndex="code"
              key="code"
              width={130}
              render={(code: string) => <Tag color="blue" className="font-mono font-bold">{code}</Tag>}
            />
            <Column title="Mô tả" dataIndex="description" key="description" width={180} ellipsis />
            <Column
              title="Loại"
              dataIndex="discount_type"
              key="discount_type"
              width={100}
              render={(type: string) => (
                <Tag color={type === 'percent' ? 'green' : 'orange'}>
                  {type === 'percent' ? 'Phần trăm' : 'Cố định'}
                </Tag>
              )}
            />
            <Column
              title="Giá trị"
              key="discount_value"
              width={120}
              render={(_: any, record: Discount) =>
                record.discount_type === 'percent'
                  ? `${record.discount_value}%`
                  : `${record.discount_value.toLocaleString('vi-VN')}đ`
              }
            />
            <Column
              title="Đơn tối thiểu"
              dataIndex="min_order_value"
              key="min_order_value"
              width={140}
              render={(val: number) => `${val.toLocaleString('vi-VN')}đ`}
            />
            <Column
              title="Giảm tối đa"
              dataIndex="max_discount"
              key="max_discount"
              width={130}
              render={(val: number | null) => val ? `${val.toLocaleString('vi-VN')}đ` : '—'}
            />
            <Column
              title="Đã dùng / Giới hạn"
              key="usage"
              width={140}
              render={(_: any, record: Discount) =>
                `${record.used_count} / ${record.usage_limit ?? '∞'}`
              }
            />
            <Column
              title="Trạng thái"
              dataIndex="is_active"
              key="is_active"
              width={110}
              render={(active: boolean) => (
                <Tag color={active ? 'green' : 'red'}>
                  {active ? 'Hoạt động' : 'Tắt'}
                </Tag>
              )}
            />
            <Column
              title="Ngày bắt đầu"
              dataIndex="start_date"
              key="start_date"
              width={160}
              render={(date: string | null) => date ? formatDate(date) : '—'}
            />
            <Column
              title="Ngày kết thúc"
              dataIndex="end_date"
              key="end_date"
              width={160}
              render={(date: string | null) => date ? formatDate(date) : '—'}
            />
            <Column
              title="Tùy Chỉnh"
              key="action"
              width={160}
              fixed="right"
              render={(_: any, record: Discount) => (
                <Space size="middle">
                  <Button type="primary" onClick={() => handleEdit(record)}>
                    Sửa
                  </Button>
                  <Popconfirm
                    title="Xóa mã giảm giá"
                    description="Bạn có chắc chắn muốn xóa mã giảm giá này?"
                    onConfirm={() => handleDelete(record.id)}
                    okText="Có"
                    cancelText="Không"
                    okButtonProps={{ danger: true }}
                  >
                    <Button danger>Xóa</Button>
                  </Popconfirm>
                </Space>
              )}
            />
          </Table>

          <Modal
            title={editingId ? 'Cập Nhật Mã Giảm Giá' : 'Thêm Mã Giảm Giá'}
            open={isModalVisible}
            onOk={handleModalOk}
            onCancel={() => setIsModalVisible(false)}
            okText={editingId ? 'Cập Nhật' : 'Thêm'}
            cancelText="Hủy"
            width={600}
            confirmLoading={createMutation.isPending || updateMutation.isPending}
          >
            <Form form={form} layout="vertical" style={{ marginTop: 20 }}>
              <Form.Item
                label="Mã giảm giá"
                name="code"
                rules={[{ required: true, message: 'Vui lòng nhập mã giảm giá' }]}
              >
                <Input
                  placeholder="VD: SALE20, FREESHIP..."
                  style={{ textTransform: 'uppercase' }}
                />
              </Form.Item>

              <Form.Item label="Mô tả" name="description">
                <Input.TextArea placeholder="Mô tả mã giảm giá" rows={2} />
              </Form.Item>

              <div className="grid grid-cols-2 gap-4">
                <Form.Item
                  label="Loại giảm giá"
                  name="discount_type"
                  rules={[{ required: true, message: 'Vui lòng chọn loại' }]}
                >
                  <Select>
                    <Select.Option value="percent">Phần trăm (%)</Select.Option>
                    <Select.Option value="fixed">Số tiền cố định (đ)</Select.Option>
                  </Select>
                </Form.Item>

                <Form.Item
                  label="Giá trị giảm"
                  name="discount_value"
                  rules={[
                    { required: true, message: 'Vui lòng nhập giá trị' },
                    {
                      validator: (_, value) => {
                        if (discountType === 'percent' && value > 100) {
                          return Promise.reject('Phần trăm tối đa 100%')
                        }
                        if (value < 0) return Promise.reject('Giá trị không được âm')
                        return Promise.resolve()
                      },
                    },
                  ]}
                >
                  <InputNumber
                    className="w-full"
                    min={0}
                    max={discountType === 'percent' ? 100 : undefined}
                    addonAfter={discountType === 'percent' ? '%' : 'đ'}
                    formatter={(value) =>
                      discountType === 'fixed'
                        ? `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')
                        : `${value}`
                    }
                  />
                </Form.Item>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <Form.Item label="Đơn hàng tối thiểu (đ)" name="min_order_value">
                  <InputNumber
                    className="w-full"
                    min={0}
                    formatter={(value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                    addonAfter="đ"
                  />
                </Form.Item>

                {discountType === 'percent' && (
                  <Form.Item label="Giảm tối đa (đ)" name="max_discount">
                    <InputNumber
                      className="w-full"
                      min={0}
                      formatter={(value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                      addonAfter="đ"
                    />
                  </Form.Item>
                )}

                <Form.Item label="Giới hạn lượt sử dụng" name="usage_limit">
                  <InputNumber className="w-full" min={1} placeholder="Không giới hạn" />
                </Form.Item>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <Form.Item label="Ngày bắt đầu" name="start_date">
                  <DatePicker
                    className="w-full"
                    showTime
                    format="DD/MM/YYYY HH:mm"
                    placeholder="Chọn ngày bắt đầu"
                  />
                </Form.Item>

                <Form.Item label="Ngày kết thúc" name="end_date">
                  <DatePicker
                    className="w-full"
                    showTime
                    format="DD/MM/YYYY HH:mm"
                    placeholder="Chọn ngày kết thúc"
                  />
                </Form.Item>
              </div>

              <Form.Item label="Trạng thái" name="is_active" valuePropName="checked">
                <Switch checkedChildren="Hoạt động" unCheckedChildren="Tắt" />
              </Form.Item>
            </Form>
          </Modal>
        </>
      )}
    </>
  )
}
