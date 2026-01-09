from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4
from datetime import datetime

class OrderDetailBase(SQLModel):
    order_id: UUID = Field(foreign_key="order.id", unique=True)

class OrderDetailIn(OrderDetailBase):
    pass

class OrderDetailOut(OrderDetailBase):
    id: UUID
    create_at: datetime
    update_at: datetime

class OrderDetail(OrderDetailBase, table=True):
    __tablename__ = 'order_detail'
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    create_at: datetime = Field(default_factory=datetime.now)
    update_at: datetime = Field(default_factory=datetime.now)
    
    # Relationship
    order: "Order" = Relationship(back_populates="order_detail")