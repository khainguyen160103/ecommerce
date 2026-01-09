from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4
from datetime import datetime

class OrderBase(SQLModel):
    user_id: UUID = Field(foreign_key="user.id")
    payment_id: UUID | None = Field(default=None, foreign_key="payment_detail.id")
    total: int

class OrderIn(OrderBase):
    pass

class OrderOut(OrderBase):
    id: UUID
    create_at: datetime
    update_at: datetime

class Order(OrderBase, table=True):
    __tablename__ = 'order'
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    create_at: datetime = Field(default_factory=datetime.now)
    update_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    order_items: list["OrderItem"] = Relationship(back_populates="order")
    order_detail: "OrderDetail" = Relationship(back_populates="order")