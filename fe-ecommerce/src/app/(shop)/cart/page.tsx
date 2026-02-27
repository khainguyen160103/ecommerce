'use client'

import { useState } from 'react'
import { Button, Row, Col, Card, Checkbox, InputNumber, Empty, Divider, message, Spin } from 'antd'
import { DeleteOutlined, ShoppingCartOutlined } from '@ant-design/icons'
import Image from 'next/image'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useCart } from '@/hook/useCart'
import { Authorization, TokenService } from '@/utils/auth.utils'
import { useCartItems } from '@/hook/useCartItems'

export default function CartPage() {
  const router = useRouter()
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set())

  // Hooks
  const { useGetMyCart, useUpdateCartItem, useDeleteCartItem } = useCart()

  // Queries & Mutations
  const { data: cartData, isLoading: cartLoading } = useGetMyCart()
  const { mutate: updateItem, isPending: isUpdating } = useUpdateCartItem()
  const { mutate: deleteItem, isPending: isDeleting } = useDeleteCartItem()

  // Lấy thông tin sản phẩm từ product_id và detail_id
  const { items: cartItems, isLoading: isLoadingProducts } = useCartItems(cartData?.items)

  const selectAll = selectedItems.size === cartItems.length && cartItems.length > 0

  // Handle select item
  const handleSelectItem = (id: string) => {
    const newSelected = new Set(selectedItems)
    if (newSelected.has(id)) {
      newSelected.delete(id)
    } else {
      newSelected.add(id)
    }
    setSelectedItems(newSelected)
  }

  // Handle select all
  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedItems(new Set(cartItems.map((item) => item.id)))
    } else {
      setSelectedItems(new Set())
    }
  }

  // Handle quantity change
  const handleQuantityChange = (id: string, quantity: number) => {
    if (quantity < 1) return
    updateItem({ itemId: id, quantity })
  }

  // Handle delete item
  const handleDeleteItem = (id: string) => {
    deleteItem(id, {
      onSuccess: () => {
        setSelectedItems((prev) => {
          const newSet = new Set(prev)
          newSet.delete(id)
          return newSet
        })
      },
    })
  }

  // Handle checkout - redirect to checkout page
  const handleCheckout = () => {
    const token = Authorization.getToken()
    const isExpired = TokenService.isTokenExpired()

    if (!token || isExpired) {
      message.error('Vui lòng đăng nhập để tiếp tục')
      router.push('/login')
      return
    }

    if (selectedItems.size === 0) {
      message.warning('Vui lòng chọn ít nhất một sản phẩm')
      return
    }

    router.push(`/checkout?item_ids=${Array.from(selectedItems).join(',')}`)
  }

  // Calculate totals
  const selectedCartItems = cartItems.filter((item) => selectedItems.has(item.id))
  const totalPrice = selectedCartItems.reduce((sum, item) => sum + item.price * item.quantity, 0)
  const totalItems = selectedCartItems.reduce((sum, item) => sum + item.quantity, 0)

  if (cartLoading || isLoadingProducts) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 flex items-center justify-center">
        <Spin size="large" />
      </div>
    )
  }

  if (cartItems.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-6xl mx-auto px-4">
          <Empty description="Giỏ hàng của bạn trống" style={{ marginTop: '100px' }}>
            <Link href="/">
              <Button type="primary" size="large">
                Tiếp tục mua sắm
              </Button>
            </Link>
          </Empty>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Giỏ hàng ({cartItems.length})</h1>
        </div>

        <Row gutter={[24, 24]}>
          {/* Cart Items */}
          <Col xs={24} lg={16}>
            <Card className="shadow-sm">
              {/* Table Header */}
              <div className="mb-4 pb-4 border-b border-gray-200">
                <Row align="middle" className="text-gray-600 text-sm font-medium">
                  <Col span={1}>
                    <Checkbox checked={selectAll} onChange={(e) => handleSelectAll(e.target.checked)} />
                  </Col>
                  <Col span={15}>Sản Phẩm</Col>
                  <Col span={2}>Đơn Giá</Col>
                  <Col span={3}>Số Lượng</Col>
                  <Col span={2}>Thao Tác</Col>
                </Row>
              </div>

              {/* Cart Items List */}
              <div className="space-y-4">
                {cartItems.map((item: any) => (
                  <div key={item.id} className="pb-4 border-b border-gray-200 last:border-b-0">
                    {/* Product Item */}
                    <Row align="middle" gutter={[16, 16]}>
                      <Col span={1}>
                        <Checkbox
                          checked={selectedItems.has(item.id)}
                          onChange={() => handleSelectItem(item.id)}
                        />
                      </Col>

                      {/* Product Info */}
                      <Col span={15}>
                        <div className="flex gap-4">
                          <div className="w-20 h-20 bg-gray-200 rounded shrink-0 overflow-hidden">
                            {item.image ? (
                              <Image
                                src={item.image}
                                alt={item.product_name || 'Sản phẩm'}
                                width={80}
                                height={80}
                                className="object-cover rounded w-full h-full"
                              />
                            ) : (
                              <div className="w-full h-full flex items-center justify-center text-gray-400 text-xs">
                                No img
                              </div>
                            )}
                          </div>
                          <div className="flex-1">
                            <Link href={`/product/${item.productId}`}>
                              <p className="text-sm line-clamp-2 text-gray-800 font-medium hover:text-blue-600 cursor-pointer">
                                {item.product_name || 'Sản phẩm'}
                              </p>
                            </Link>
                            {(item.color || item.size) && (
                              <p className="text-xs text-gray-500 mt-1">
                                Phân loại: {[item.color, item.size].filter(Boolean).join(' / ')}
                              </p>
                            )}
                          </div>
                        </div>
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
                            className="px-2 py-1 text-gray-600 hover:bg-gray-100"
                            onClick={() => handleQuantityChange(item.id, item.quantity - 1)}
                            disabled={isUpdating}
                          >
                            −
                          </button>
                          <InputNumber
                            min={1}
                            value={item.quantity}
                            onChange={(val) => handleQuantityChange(item.id, val || 1)}
                            controls={false}
                            className="border-0 text-center w-12"
                            disabled={isUpdating}
                          />
                          <button
                            className="px-2 py-1 text-gray-600 hover:bg-gray-100"
                            onClick={() => handleQuantityChange(item.id, item.quantity + 1)}
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
                          onClick={() => handleDeleteItem(item.id)}
                          loading={isDeleting}
                        />
                      </Col>
                    </Row>
                  </div>
                ))}
              </div>
            </Card>
          </Col>

          {/* Summary */}
          <Col xs={24} lg={8}>
            <Card className="shadow-sm sticky top-4">
              <div className="space-y-4">
                {/* Summary Details */}
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

                {/* Checkout Button */}
                <Button
                  type="primary"
                  danger
                  size="large"
                  block
                  disabled={selectedItems.size === 0}
                  onClick={handleCheckout}
                  icon={<ShoppingCartOutlined />}
                >
                  Thanh toán ({selectedItems.size})
                </Button>

                {/* Continue Shopping */}
                <Link href="/">
                  <Button size="large" block>
                    Tiếp tục mua sắm
                  </Button>
                </Link>
              </div>
            </Card>
          </Col>
        </Row>
      </div>
    </div>
  )
}