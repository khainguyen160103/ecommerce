from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .product_model import Product
    from .cart_item_model import CartItem
    
class ProductDetailBase(SQLModel):
    color: str | None = None
    size: str | None = None
    stock: int = 0
    weight: float | None = None
    length: float | None = None
    width: float | None = None
    height: float | None = None

class ProductDetailIn(ProductDetailBase):
    pass

class ProductDetailOut(ProductDetailBase):
    id: UUID
    create_at: datetime
    update_at: datetime

class ProductDetail(ProductDetailBase, table=True):
    __tablename__ = 'product_detail'

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    create_at: datetime = Field(default_factory=datetime.now)
    update_at: datetime = Field(default_factory=datetime.now)
    product_id: UUID = Field(
        foreign_key="product.id", ondelete="CASCADE", nullable=False
    )

    # Relationships
    product: "Product" = Relationship(back_populates="product_details")
    cart_items: list["CartItem"] = Relationship(back_populates="product_detail") 