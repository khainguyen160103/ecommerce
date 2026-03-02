from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4
from datetime import datetime
from app.utils.timezone import vn_now

class PaymentDetailBase(SQLModel):
    # order_id: UUID = Field(foreign_key="order.id")
    amount: int
    provider: str
    status: str = "pending"

class PaymentDetailIn(PaymentDetailBase):
    pass

class PaymentDetailOut(PaymentDetailBase):
    id: UUID
    create_at: datetime
    update_at: datetime

class PaymentDetail(PaymentDetailBase, table=True):
    __tablename__ = 'payment_detail'
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    create_at: datetime = Field(default_factory=vn_now)
    update_at: datetime = Field(default_factory=vn_now)