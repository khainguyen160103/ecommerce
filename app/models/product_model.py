from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4
from datetime import datetime

class ProductBase(SQLModel):
    name: str = Field(nullable=False)
    description: str | None = None
    cover: str | None = None
    price: str | None = None
    category_id: UUID = Field(foreign_key="category.id")

class ProductIn(ProductBase):
    pass

class ProductOut(ProductBase):
    id: UUID
    create_at: datetime
    update_at: datetime

class Product(ProductBase, table=True):
    __tablename__ = 'product'
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    create_at: datetime = Field(default_factory=datetime.now)
    update_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    category: "Category" = Relationship(back_populates="products")
    product_details: list["ProductDetail"] = Relationship(back_populates="product")
    cart_items: list["CartItem"] = Relationship(back_populates="product")
    order_items: list["OrderItem"] = Relationship(back_populates="product")