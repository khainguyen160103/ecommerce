from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cart_model import Cart
    from .product_model import Product
    from .product_detail_model import ProductDetail


class CartItemBase(SQLModel):
    cart_id: UUID = Field(foreign_key="cart.id")
    product_id: UUID = Field(foreign_key="product.id")
    detail_id: UUID = Field(foreign_key="product_detail.id")
    quantity: int

class CartItemIn(CartItemBase):
    pass

class CartItemOut(CartItemBase):
    id: UUID
    create_at: datetime
    update_at: datetime

class CartItem(CartItemBase, table=True):
    __tablename__ = 'cart_item'
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    create_at: datetime = Field(default_factory=datetime.now)
    update_at: datetime = Field(default_factory=datetime.now)
    # Relationships
    cart: "Cart" = Relationship(back_populates="cart_items")
    product: "Product" = Relationship(back_populates="cart_items")
    product_detail: "ProductDetail" = Relationship(back_populates="cart_items")
