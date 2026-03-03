"""
Discount Repository - Xử lý tất cả query liên quan đến mã giảm giá
"""
from sqlmodel import Session, select
from typing import List
from uuid import UUID
from datetime import datetime

from app.models.discount_model import Discount, DiscountIn, DiscountUpdate, DiscountOut
from app.utils.timezone import vn_now


class DiscountRepository:
    """Repository quản lý mã giảm giá"""

    def get_all(self, session: Session) -> List[Discount]:
        """Lấy tất cả mã giảm giá"""
        return session.exec(select(Discount).order_by(Discount.create_at.desc())).all()  # type: ignore[union-attr]  # noqa  # pylint: disable=no-member

    def get_by_id(self, discount_id: UUID, session: Session) -> Discount | None:
        """Lấy mã giảm giá theo ID"""
        return session.exec(
            select(Discount).where(Discount.id == discount_id)
        ).first()

    def get_by_code(self, code: str, session: Session) -> Discount | None:
        """Lấy mã giảm giá theo code"""
        return session.exec(
            select(Discount).where(Discount.code == code)
        ).first()

    def create(self, data: DiscountIn, session: Session) -> Discount:
        """Tạo mã giảm giá mới"""
        discount = Discount(**data.model_dump())
        session.add(discount)
        session.commit()
        session.refresh(discount)
        return discount

    def update(self, discount: Discount, data: DiscountUpdate, session: Session) -> Discount:
        """Cập nhật mã giảm giá"""
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(discount, key, value)
        discount.update_at = vn_now()
        session.add(discount)
        session.commit()
        session.refresh(discount)
        return discount

    def delete(self, discount: Discount, session: Session) -> None:
        """Xóa mã giảm giá"""
        session.delete(discount)
        session.commit()

    def increment_used_count(self, discount: Discount, session: Session) -> Discount:
        """Tăng số lần sử dụng"""
        discount.used_count += 1
        discount.update_at = vn_now()
        session.add(discount)
        session.commit()
        session.refresh(discount)
        return discount
