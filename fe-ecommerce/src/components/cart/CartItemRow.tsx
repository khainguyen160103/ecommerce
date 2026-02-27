'use client'

import { memo, useState, useCallback } from 'react'
import { Row, Col, Checkbox, InputNumber, Button } from 'antd'
import { DeleteOutlined, ShoppingOutlined } from '@ant-design/icons'
import Image from 'next/image'
import Link from 'next/link'

interface CartItemRowProps {
  item: any
  selected: boolean
  onSelect: (id: string) => void
  onQuantityChange: (id: string, quantity: number) => void
  onDelete: (id: string) => void
  isUpdating: boolean
  isDeleting: boolean
}

const CartItemRow = memo(function CartItemRow({
  item,
  selected,
  onSelect,
  onQuantityChange,
  onDelete,
  isUpdating,
  isDeleting,
}: CartItemRowProps) {
  // Local quantity để UI phản hồi ngay, không chờ API
  const [localQty, setLocalQty] = useState(item.quantity)

  // Sync lại khi server trả về giá trị mới
  if (item.quantity !== localQty && !isUpdating) {
    setLocalQty(item.quantity)
  }
  
  const handleDecrease = useCallback(() => {
    if (localQty <= 1 || isUpdating) return
    const newQty = localQty - 1
    setLocalQty(newQty)
    onQuantityChange(item.id, newQty)
  }, [localQty, isUpdating, item.id, onQuantityChange])

  const handleIncrease = useCallback(() => {
    if (isUpdating) return
    const newQty = localQty + 1
    setLocalQty(newQty)
    onQuantityChange(item.id, newQty)
  }, [localQty, isUpdating, item.id, onQuantityChange])

  const handleInputChange = useCallback(
    (val: number | null) => {
      const newQty = val || 1
      setLocalQty(newQty)
      onQuantityChange(item.id, newQty)
    },
    [item.id, onQuantityChange]
  )

  return (
    <div className="pb-4 border-b border-gray-200 last:border-b-0">
      {/* Shop Name */}
      <div className="mb-3 text-sm text-gray-600">
        <ShoppingOutlined className="mr-2" />
        {item.shop}
      </div>

      {/* Product Item */}
      <Row align="middle" gutter={[16, 16]}>
        <Col span={1}>
          <Checkbox checked={selected} onChange={() => onSelect(item.id)} />
        </Col>

        {/* Product Info */}
        <Col span={15}>
          <Link href={`/product/${item.product_id}`}>
            <div className="flex gap-4 cursor-pointer">
              <div className="w-20 h-20 bg-gray-200 rounded shrink-0 overflow-hidden">
                <Image
                  src={item.image}
                  alt={item.productName}
                  width={80}
                  height={80}
                  className="object-cover rounded w-full h-full"
                />
              </div>
              <div className="flex-1">
                <p className="text-sm line-clamp-2 text-gray-800 font-medium hover:text-blue-600">
                  {item.productName}
                </p>
                {item.variantInfo && (
                  <p className="text-xs text-gray-500 mt-1">Phân loại: {item.variantInfo}</p>
                )}
                {item.sku && (
                  <p className="text-xs text-gray-400 mt-0.5">SKU: {item.sku}</p>
                )}
              </div>
            </div>
          </Link>
        </Col>

        {/* Price */}
        <Col span={2} className="text-right">
          <p className="text-orange-600 font-semibold">
            {item.price.toLocaleString('vi-VN')}₫
          </p>
        </Col>

        {/* Quantity */}
        <Col span={3}>
          <div className="flex items-center border border-gray-300 rounded">
            <button
              className="px-2 py-1 text-gray-600 hover:bg-gray-100 disabled:opacity-50"
              onClick={handleDecrease}
              disabled={isUpdating || localQty <= 1}
            >
              −
            </button>
            <InputNumber
              min={1}
              value={localQty}
              onChange={handleInputChange}
              controls={false}
              className="border-0 text-center w-12"
              disabled={isUpdating}
            />
            <button
              className="px-2 py-1 text-gray-600 hover:bg-gray-100 disabled:opacity-50"
              onClick={handleIncrease}
              disabled={isUpdating}
            >
              +
            </button>
          </div>
        </Col>

        {/* Action */}
        <Col span={2} className="text-center">
          <Button
            type="text"
            danger
            icon={<DeleteOutlined />}
            onClick={() => onDelete(item.id)}
            loading={isDeleting}
          />
        </Col>
      </Row>
    </div>
  )
})

export default CartItemRow
