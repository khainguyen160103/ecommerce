from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel, ConfigDict
from fastapi import UploadFile
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .category_model import Category
    from .product_detail_model import ProductDetail
    from .product_image_model import ProductImage
    from .cart_item_model import CartItem
    from .order_item_model import OrderItem


class ProductBase(SQLModel):
    name: str = Field(nullable=False)
    description: str | None = None
    # cover: str | None = None
    price: str | None = None
    category_id: UUID = Field(foreign_key="category.id")


class ProductIn(ProductBase):
    file: Optional[list[UploadFile]]


# ===== RESPONSE MODELS (Pure Pydantic - không kế thừa SQLModel) =====


class ProductResponseOut(BaseModel):
    """Pure Pydantic model cho response - tránh inherit fields từ SQLModel"""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    description: Optional[str] = None
    price: Optional[str] = None
    category_id: UUID
    create_at: datetime
    update_at: datetime


class ProductOut(ProductBase):
    id: UUID
    create_at: datetime
    update_at: datetime


class ProductDetailResponse(SQLModel):
    """Sử dụng cho response"""

    id: UUID
    size: Optional[str] = None
    color: Optional[str] = None
    quantity: int


class ProductImageResponse(SQLModel):
    """Sử dụng cho response"""

    id: UUID
    url: str
    thumbnail_url: Optional[str] = None


class ProductDetailOut(BaseModel):
    """Response cho chi tiết sản phẩm - sử dụng BaseModel để tránh inherit fields từ SQLModel"""

    model_config = ConfigDict(from_attributes=True)
    product: ProductResponseOut
    details: list = []
    images: list = []


class Product(ProductBase, table=True):
    __tablename__ = "product"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    create_at: datetime = Field(default_factory=datetime.now)
    update_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    category: Optional["Category"] = Relationship(back_populates="products")
    product_details: list["ProductDetail"] = Relationship(
        back_populates="product", sa_relationship_kwargs={"passive_deletes": True}
    )
    cart_items: list["CartItem"] = Relationship(back_populates="product")
    order_items: list["OrderItem"] = Relationship(back_populates="product")
    images: list["ProductImage"] = Relationship(
        back_populates="product", sa_relationship_kwargs={"passive_deletes": True}
    )
