from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .user_model import User
    from .order_item_model import OrderItem

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
    status: str
    # GoShip shipping fields
    shipping_code: str | None = Field(default=None)  # GoShip shipment ID
    carrier: str | None = Field(default=None)  # Tên đơn vị vận chuyển
    tracking_number: str | None = Field(default=None)  # Mã vận đơn
    shipping_fee: int = Field(default=0)  # Phí vận chuyển
    rate_id: str | None = Field(default=None)  # GoShip rate ID đã chọn
    # Relationships
    user: Optional["User"] = Relationship(back_populates="order")
    order_items: list["OrderItem"] = Relationship(back_populates="order")
    # order_detail: "OrderDetail" = Relationship(back_populates="order")