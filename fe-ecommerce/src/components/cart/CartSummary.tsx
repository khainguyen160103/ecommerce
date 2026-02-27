'use client'

import { memo } from 'react'
import { Button, Card, Divider } from 'antd'
import { ShoppingCartOutlined } from '@ant-design/icons'
import Link from 'next/link'

interface CartSummaryProps {
  totalPrice: number
  totalItems: number
  selectedCount: number
  isCreatingOrder: boolean
  disabled: boolean
  onCheckout: () => void
}

const CartSummary = memo(function CartSummary({
  totalPrice,
  totalItems,
  selectedCount,
  isCreatingOrder,
  disabled,
  onCheckout,
}: CartSummaryProps) {
  return (
    <Card className="shadow-sm sticky top-4">
      <div className="space-y-4">
        <div>
          <div className="flex justify-between py-2 text-sm text-gray-600">
            <span>Tổng tiền ({totalItems} sản phẩm):</span>
            <span className="text-orange-600 font-semibold text-lg">
              {totalPrice.toLocaleString('vi-VN')}₫
            </span>
          </div>

          <Divider className="my-3" />

          <div className="flex justify-between py-2 text-sm text-gray-600">
            <span>Phí vận chuyển:</span>
            <span className="text-green-600 font-medium">Miễn phí</span>
          </div>

          <Divider className="my-3" />

          <div className="flex justify-between py-2 font-semibold text-base">
            <span>Thành tiền:</span>
            <span className="text-orange-600">
              {totalPrice.toLocaleString('vi-VN')}₫
            </span>
          </div>
        </div>

        <Button
          type="primary"
          danger
          size="large"
          block
          disabled={disabled || selectedCount === 0}
          loading={isCreatingOrder}
          onClick={onCheckout}
          icon={<ShoppingCartOutlined />}
        >
          Mua Hàng ({selectedCount})
        </Button>

        <Link href="/">
          <Button size="large" block>
            Tiếp tục mua sắm
          </Button>
        </Link>
      </div>
    </Card>
  )
})

export default CartSummary
