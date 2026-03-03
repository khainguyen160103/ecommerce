'use client'
import { useState, useEffect } from 'react'
import Image from 'next/image'
import { useParams, useRouter } from 'next/navigation'
import { Button, Card, Row, Col, Spin, message, InputNumber, Space, Divider, Tag, Breadcrumb, Radio } from 'antd'
import { ShoppingCartOutlined, MinusOutlined, PlusOutlined } from '@ant-design/icons'
import { useProduct } from '@/hook/useProduct'
import { useCart } from '@/hook/useCart'
import Link from 'next/link'
import type { RadioChangeEvent } from 'antd'
import _ from 'lodash'
import { Product } from '@/models/product'
import { ProductDetail } from '@/models/productDetail'
import toast from 'react-hot-toast'
import ProductReviews from '@/components/product/ProductReviews'
import { Authorization } from '@/utils/auth.utils'

export default function ProductDetailPage() {
  const params = useParams()
  const router = useRouter()
  const productId = params.id as string
  const [quantity, setQuantity] = useState(1)
  const [colorSelected, setColorSelected] = useState(null)
  const [sizeSelected, setSizeSelected] = useState(null)
  const [currentUserId, setCurrentUserId] = useState<string | undefined>(undefined)

  useEffect(() => {
    const userInfo = Authorization.getUserInfor()
    if (userInfo?.id) {
      setCurrentUserId(userInfo.id)
    }
  }, [])

  const { productIdData, productDetailsData } = useProduct(productId)
  const { useGetMyCart, useAddToCart } = useCart()
  const { data: cartData } = useGetMyCart()
  const { mutate: addToCart, isPending: isAddingToCart } = useAddToCart()
  
  const product: Product | undefined = productIdData.data?.data
  const details: ProductDetail[] = productDetailsData.data?.data || []

  const colorGroupBy = _.groupBy(details, "color")
  const sizeGroupBy = _.groupBy(details, "size")
  // Get selected product detail ID
  const selectedProductDetail = colorSelected && sizeSelected 
    ? _.find(details, {
        color: colorSelected,
        size: sizeSelected
      })
    : null
  console.log(selectedProductDetail)
  const handleAddToCart = () => { 
    // Validate variant selection if product has variants
    if (details.length > 0 && (!colorSelected || !sizeSelected)) {
      message.warning('Vui lòng chọn màu sắc và kích thước')
      return
    }

    // Validate quantity
    if (quantity < 1) {
      message.warning('Số lượng phải lớn hơn 0')
      return
    }

    // Validate stock
    if (selectedProductDetail && selectedProductDetail?.stock !== null && quantity > selectedProductDetail?.stock) {
      message.error(`Chỉ còn ${selectedProductDetail.stock} sản phẩm trong kho`)
      return
    }

    // Add to cart
    if (details.length > 0 && selectedProductDetail) {
      addToCart(
        {
          product_id: product?.id,
          detail_id: selectedProductDetail.id,
          quantity: quantity,
          cart_id: cartData?.cart.id
        },
        {
          onSuccess: () => {
            setQuantity(1)
          },
        }
      )
    } else { 
      message.error('Không tìm thấy thông tin sản phẩm')
    }
  }
  
  const handleBuyNow = () => {
    // Validate variant selection if product has variants
    if (details.length > 0 && (!colorSelected || !sizeSelected)) {
      message.warning('Vui lòng chọn màu sắc và kích thước')
      return
    }

    // Validate quantity
    if (selectedProductDetail && selectedProductDetail?.stock !== null && quantity > selectedProductDetail?.stock) {
      message.error(`Chỉ còn ${selectedProductDetail.stock} sản phẩm trong kho`)
      return
    }

    if (quantity < 1) {
      message.warning('Số lượng phải lớn hơn 0')
      return
    }

    // Add to cart and redirect to cart page
    if (details.length > 0 && selectedProductDetail) {
      addToCart(
        {
          product_id: product?.id, 
          cart_id: cartData?.cart.id,
          detail_id: selectedProductDetail.id,
          quantity: quantity,
        },
        {
          onSuccess: () => {
            setQuantity(1)
            router.push('/cart')
          },
        }
      )
    } else {
      message.error('Không tìm thấy thông tin sản phẩm')
    }
  }

  const handleRadioColorOnChange = (e: RadioChangeEvent) => {
    console.log("value: ", e.target.value)
    setColorSelected(e.target.value)
  }

  const handleRadioSizeOnChange = (e: RadioChangeEvent) => {
    console.log("value: ", e.target.value)
    setSizeSelected(e.target.value)

  }

  const handleQuantityPlus = () => {
    if (selectedProductDetail && quantity < selectedProductDetail.stock) {
      setQuantity(quantity + 1)
    } else {
      toast.error("Sản phẩm đã hết hàng")
    }
  }
  if (productIdData.isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spin size="large" />
      </div>
    )
  }

  if (!product) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-lg text-gray-500 mb-4">Sản phẩm không tồn tại</p>
          <Button type="primary" onClick={() => router.push('/')}>
            Quay lại trang chủ
          </Button>
        </div>
      </div>
    )
  }
  console.log("select item: ", selectedProductDetail)
  return (
    <>
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-6xl mx-auto px-4">
          {/* Breadcrumb */}
          <Breadcrumb
            className="mb-6"
            items={[
              {
                title: <Link href="/">Trang chủ</Link>,
              },
              {
                title: 'Chi tiết sản phẩm',
              },
            ]}
          />

          {/* Product Detail */}
          <Card className="shadow-sm mb-6">
            <Row gutter={[32, 32]}>
              {/* Product Images */}
              <Col xs={24} md={12}>
                <div className="bg-white rounded-lg overflow-hidden">
                  <div className="w-full h-96 bg-gray-200 flex items-center justify-center">
                    {product?.images?.[0] && (
                      <Image
                        src={product.images[0].url}
                        alt={product.name}
                        width={400}
                        height={400}
                        className="object-cover"
                      />
                    )}
                  </div>

                  {/* Thumbnail Images */}
                  <div className="mt-4 flex gap-2">
                    <div
                      className="w-20 h-20 bg-gray-200 rounded cursor-pointer hover:opacity-75 flex items-center justify-center"
                    >
                      {product?.images?.[0] && (<Image
                        src={product.images[0].thumbnail_url}
                        alt="thumbnail"
                        width={80}
                        height={80}
                        className="object-cover"
                      />)}
                    </div>
                  </div>
                </div>
                <div className='mt-13'> 

                <Card title="Chính sách bán hàng" className="shadow-sm">
                  <div className="space-y-2 text-sm text-gray-700">
                    <p>✓ Sản phẩm chính hãng 100%</p>
                    <p>✓ Hỗ trợ khách hàng 24/7</p>
                    <p>✓ Bảo hành 12 tháng</p>
                    <p>✓ Giao hàng nhanh chóng</p>
                  </div>
                </Card>
                </div>
              </Col>

              {/* Product Info */}
              <Col xs={24} md={12}>
                <div className="space-y-6">
                  <div>
                    <h1 className="text-3xl font-bold mb-2">{product.name}</h1>
                    <div className="flex items-center gap-4">
                      <Tag color={details && details.length > 0 ? "blue" : "orange"}>
                        {details && details.length > 0 ? "Còn hàng" : "Hết Hàng"}
                      </Tag>
                    </div>
                  </div>

                  {/* Price */}
                  <div className="border-y border-gray-200 py-4">
                    <div className="flex items-baseline gap-4">
                      <span className="text-3xl font-bold text-red-500">
                        {parseFloat(product.price).toLocaleString('vi-VN')} ₫
                      </span>
                      <span className="text-lg text-gray-400 line-through">
                        {(parseFloat(product.price) * 1.2).toLocaleString('vi-VN')} ₫
                      </span>
                      <Tag color="red">-17%</Tag>
                    </div>
                  </div>

                  {/* Description */}
                  <div>
                    <h3 className="font-semibold mb-2">Mô tả sản phẩm</h3>
                    <p className="text-gray-600 leading-relaxed">{product.description}</p>
                  </div>

                  {/* Variants */}
                  {details.length > 0 && (
                    <>
                      <Row>
                        <Col flex="100px">Màu sắc</Col>
                        <Col flex="auto">
                          <Radio.Group onChange={handleRadioColorOnChange}>
                            {Object.keys(colorGroupBy).map((color, index) => (
                              <Radio.Button key={index} value={color}>
                                {color}
                              </Radio.Button>
                            )
                            )}
                          </Radio.Group>
                        </Col>
                      </Row>
                      <Row>
                        <Col flex="100px">Kích thước</Col>
                        <Col flex="auto">
                          <Radio.Group onChange={handleRadioSizeOnChange}>
                            {Object.keys(sizeGroupBy).map((size, index) => (
                              <Radio.Button key={index} value={size}>
                                {size}
                              </Radio.Button>
                            )
                            )}
                          </Radio.Group>
                        </Col>
                      </Row>
                    </>
                  )}

                  {/* Quantity & Actions */}
                  <div>
                    <h3 className="font-semibold mb-3">Số lượng</h3>
                    <div className="flex items-center gap-4 mb-6">
                      <div className="flex items-center border border-gray-300 rounded">
                        <Button
                          type="text"
                          icon={<MinusOutlined />}
                          onClick={() => setQuantity(Math.max(1, quantity - 1))}
                        />
                        <InputNumber
                          value={quantity}
                          onChange={(val) => setQuantity(val || 1)}
                          min={1}
                          max={100}
                          readOnly
                          controls={false}
                          className="border-0"
                          style={{ width: '60px', textAlign: 'center' }}
                        />

                        <Button
                          type="text"
                          icon={<PlusOutlined />}

                          onClick={handleQuantityPlus}
                        />
                      </div>
                      <span className="text-gray-600">Còn {selectedProductDetail ? selectedProductDetail.stock : 0}  sản phẩm</span>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <Space style={{ width: '100%' }} orientation="vertical" size="large">
                    <Button
                      type="primary"
                      size="large"
                      icon={<ShoppingCartOutlined />}
                      onClick={handleAddToCart}
                      loading={isAddingToCart}
                      block
                    >
                      Thêm vào giỏ hàng
                    </Button>
                    <Button
                      type="primary"
                      danger
                      size="large"
                      onClick={handleBuyNow}
                      loading={isAddingToCart}
                      block
                    >
                      Mua ngay
                    </Button>
                  </Space>

                  {/* Shipping Info */}


                  <Card
                    className="shadow-sm border-blue-200 bg-blue-50"
                    style={{ padding: '24px' }}
                  >
                    <div className="space-y-4">
                      <div className="flex items-start gap-4">
                        <span className="text-2xl">📦</span>
                        <div>
                          <p className="font-semibold text-gray-800 mb-1">Miễn phí vận chuyển</p>
                          <p className="text-sm text-gray-600">cho đơn hàng trên 100.000 ₫</p>
                        </div>
                      </div>

                      <Divider className="my-2" />

                      <div className="flex items-start gap-4">
                        <span className="text-2xl">✓</span>
                        <div>
                          <p className="font-semibold text-gray-800 mb-1">Hoàn tiền 100%</p>
                          <p className="text-sm text-gray-600">nếu sản phẩm không như mô tả</p>
                        </div>
                      </div>

                      <Divider className="my-2" />

                      <div className="flex items-start gap-4">
                        <span className="text-2xl">🛡️</span>
                        <div>
                          <p className="font-semibold text-gray-800 mb-1">Bảo vệ người mua</p>
                          <p className="text-sm text-gray-600">được đảm bảo 100% an toàn</p>
                        </div>
                      </div>
                    </div>
                  </Card>
                </div>
              </Col>
            </Row>
          </Card>

          {/* Additional Info */}

          {/* Product Reviews */}
          <div className="mt-6">
            <ProductReviews productId={productId} currentUserId={currentUserId} />
          </div>

        </div>
      </div>
    </>
  )
}
