from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4
from datetime import datetime

class OrderItemBase(SQLModel):
    order_id: UUID = Field(foreign_key="order.id")
    product_id: UUID = Field(foreign_key="product.id")
    quantity: int

class OrderItemIn(OrderItemBase):
    pass

class OrderItemOut(OrderItemBase):
    id: UUID
    create_at: datetime
    update_at: datetime

class OrderItem(OrderItemBase, table=True):
    __tablename__ = 'order_item'
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    create_at: datetime = Field(default_factory=datetime.now)
    update_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    order: "Order" = Relationship(back_populates="order_items")
    product: "Product" = Relationship(back_populates="order_items")