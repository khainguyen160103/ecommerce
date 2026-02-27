# app/models/__init__.py

# Category Models
from .category_model import Category, CategoryBase, CategoryIn, CategoryOut

# Product Models
from .product_model import (
    Product, 
    ProductBase, 
    ProductIn, 
    ProductOut,
    ProductResponseOut,
    ProductDetailResponse,
    ProductDetailOut
)

# Product Detail Models
from .product_detail_model import (
    ProductDetail,
    ProductDetailBase,
    ProductDetailIn,
    ProductDetailOut as ProductDetailOutputModel
)

# Product Image Models
from .product_image_model import ProductImage

# User Models
from .user_model import User, UserBase, UserIn, UserOut

# Role Models
from .role_model import Role

# Address Models
from .adress_model import Address, AddressBase, AddressIn, AddressOut

# Cart Models
from .cart_model import Cart, CartBase, CartIn, CartOut

# Cart Item Models
from .cart_item_model import CartItem, CartItemBase, CartItemIn, CartItemOut

# Order Models
from .order_model import Order, OrderBase, OrderIn, OrderOut

# Order Item Models
from .order_item_model import OrderItem, OrderItemBase, OrderItemIn, OrderItemOut

# Payment Detail Models
from .payment_detail_model import PaymentDetail, PaymentDetailBase, PaymentDetailIn, PaymentDetailOut

# Export all
__all__ = [
    # Category
    "Category", "CategoryBase", "CategoryIn", "CategoryOut",
    # Product
    "Product", "ProductBase", "ProductIn", "ProductOut", "ProductResponseOut", "ProductDetailResponse", "ProductDetailOut",
    # Product Detail
    "ProductDetail", "ProductDetailBase", "ProductDetailIn", "ProductDetailOutputModel",
    # Product Image
    "ProductImage",
    # User
    "User", "UserBase", "UserIn", "UserOut",
    # Role
    "Role",
    # Address
    "Address", "AddressBase", "AddressIn", "AddressOut",
    # Cart
    "Cart", "CartBase", "CartIn", "CartOut",
    # Cart Item
    "CartItem", "CartItemBase", "CartItemIn", "CartItemOut",
    # Order
    "Order", "OrderBase", "OrderIn", "OrderOut",
    # Order Item
    "OrderItem", "OrderItemBase", "OrderItemIn", "OrderItemOut",
    # Payment Detail
    "PaymentDetail", "PaymentDetailBase", "PaymentDetailIn", "PaymentDetailOut",
]