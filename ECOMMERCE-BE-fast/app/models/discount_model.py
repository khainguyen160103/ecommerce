"""
Discount Model - Mã giảm giá
Hỗ trợ 2 loại: percent (%) và fixed (số tiền cố định)
"""
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from app.utils.timezone import vn_now


class DiscountBase(SQLModel):
    code: str = Field(nullable=False, unique=True, index=True)
    description: str | None = None
    discount_type: str = Field(default="percent")  # "percent" hoặc "fixed"
    discount_value: float = Field(default=0)  # Giá trị giảm (% hoặc số tiền)
    min_order_value: float = Field(default=0)  # Đơn hàng tối thiểu để áp dụng
    max_discount: float | None = Field(default=None)  # Giới hạn giảm tối đa (cho percent)
    usage_limit: int | None = Field(default=None)  # Tổng số lần sử dụng tối đa
    used_count: int = Field(default=0)  # Số lần đã sử dụng
    is_active: bool = Field(default=True)  # Trạng thái hoạt động
    start_date: datetime | None = Field(default=None)  # Ngày bắt đầu
    end_date: datetime | None = Field(default=None)  # Ngày kết thúc


class DiscountIn(SQLModel):
    code: str
    description: str | None = None
    discount_type: str = "percent"  # "percent" hoặc "fixed"
    discount_value: float = 0
    min_order_value: float = 0
    max_discount: float | None = None
    usage_limit: int | None = None
    is_active: bool = True
    start_date: datetime | None = None
    end_date: datetime | None = None


class DiscountUpdate(SQLModel):
    code: str | None = None
    description: str | None = None
    discount_type: str | None = None
    discount_value: float | None = None
    min_order_value: float | None = None
    max_discount: float | None = None
    usage_limit: int | None = None
    is_active: bool | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class DiscountOut(DiscountBase):
    id: UUID
    create_at: datetime
    update_at: datetime


class Discount(DiscountBase, table=True):
    __tablename__ = "discount"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    create_at: datetime = Field(default_factory=vn_now)
    update_at: datetime = Field(default_factory=vn_now)
