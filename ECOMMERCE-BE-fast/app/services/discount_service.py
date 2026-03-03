"""
Discount Service - Xử lý logic mã giảm giá
Admin: CRUD mã giảm giá
User: Áp dụng mã giảm giá
"""
from app.models.discount_model import Discount, DiscountIn, DiscountUpdate, DiscountOut
from app.repositories.discount_repository import DiscountRepository
from fastapi import HTTPException, status, Depends
from sqlmodel import Session
from uuid import UUID
from typing import Dict, Any, Annotated, List
from app.utils.timezone import vn_now


class DiscountService:
    """Service quản lý mã giảm giá"""

    def __init__(self, repository: Annotated[DiscountRepository, Depends()]):
        self.repository = repository

    # ==================== ADMIN FUNCTIONS ====================

    def get_all_discounts(self, session: Session) -> List[DiscountOut]:
        """[ADMIN] Lấy tất cả mã giảm giá"""
        discounts = self.repository.get_all(session)
        return [DiscountOut.model_validate(d) for d in discounts]

    def get_discount_by_id(self, discount_id: UUID, session: Session) -> DiscountOut:
        """[ADMIN] Lấy mã giảm giá theo ID"""
        discount = self.repository.get_by_id(discount_id, session)
        if not discount:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mã giảm giá không tồn tại"
            )
        return DiscountOut.model_validate(discount)

    def create_discount(self, data: DiscountIn, session: Session) -> Dict[str, Any]:
        """[ADMIN] Tạo mã giảm giá mới"""
        # Validate
        if data.discount_type not in ("percent", "fixed"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Loại giảm giá phải là 'percent' hoặc 'fixed'"
            )
        if data.discount_type == "percent" and (data.discount_value < 0 or data.discount_value > 100):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phần trăm giảm giá phải từ 0 đến 100"
            )
        if data.discount_value < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Giá trị giảm giá không được âm"
            )

        # Kiểm tra code trùng
        existing = self.repository.get_by_code(data.code.upper(), session)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã giảm giá đã tồn tại"
            )

        data.code = data.code.upper()
        discount = self.repository.create(data, session)
        return {
            "message": "Tạo mã giảm giá thành công",
            "data": DiscountOut.model_validate(discount)
        }

    def update_discount(self, discount_id: UUID, data: DiscountUpdate, session: Session) -> Dict[str, Any]:
        """[ADMIN] Cập nhật mã giảm giá"""
        discount = self.repository.get_by_id(discount_id, session)
        if not discount:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mã giảm giá không tồn tại"
            )

        # Validate
        discount_type = data.discount_type or discount.discount_type
        discount_value = data.discount_value if data.discount_value is not None else discount.discount_value

        if discount_type == "percent" and (discount_value < 0 or discount_value > 100):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phần trăm giảm giá phải từ 0 đến 100"
            )

        # Kiểm tra code trùng nếu đổi code
        if data.code and data.code.upper() != discount.code:
            existing = self.repository.get_by_code(data.code.upper(), session)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Mã giảm giá đã tồn tại"
                )
            data.code = data.code.upper()

        updated = self.repository.update(discount, data, session)
        return {
            "message": "Cập nhật mã giảm giá thành công",
            "data": DiscountOut.model_validate(updated)
        }

    def delete_discount(self, discount_id: UUID, session: Session) -> Dict[str, str]:
        """[ADMIN] Xóa mã giảm giá"""
        discount = self.repository.get_by_id(discount_id, session)
        if not discount:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mã giảm giá không tồn tại"
            )
        self.repository.delete(discount, session)
        return {"message": "Xóa mã giảm giá thành công"}

    # ==================== USER FUNCTIONS ====================

    def apply_discount(self, code: str, subtotal: float, session: Session) -> Dict[str, Any]:
        """
        [USER] Kiểm tra và tính toán giảm giá
        Args:
            code: Mã giảm giá
            subtotal: Tổng tiền đơn hàng (trước giảm giá)
            session: Database session
        Returns:
            Dict chứa thông tin giảm giá
        """
        discount = self.repository.get_by_code(code.upper(), session)
        if not discount:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mã giảm giá không tồn tại"
            )

        # Kiểm tra trạng thái
        if not discount.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã giảm giá đã hết hiệu lực"
            )

        # Kiểm tra ngày hiệu lực
        now = vn_now().replace(tzinfo=None)
        if discount.start_date and now < discount.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã giảm giá chưa có hiệu lực"
            )
        if discount.end_date and now > discount.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã giảm giá đã hết hạn"
            )

        # Kiểm tra số lần sử dụng
        if discount.usage_limit is not None and discount.used_count >= discount.usage_limit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã giảm giá đã hết lượt sử dụng"
            )

        # Kiểm tra đơn hàng tối thiểu
        if subtotal < discount.min_order_value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Đơn hàng tối thiểu {int(discount.min_order_value):,}đ để áp dụng mã này"
            )

        # Tính toán giảm giá
        if discount.discount_type == "percent":
            discount_amount = subtotal * (discount.discount_value / 100)
            if discount.max_discount is not None:
                discount_amount = min(discount_amount, discount.max_discount)
        else:  # fixed
            discount_amount = min(discount.discount_value, subtotal)

        discount_amount = round(discount_amount)

        return {
            "discount_id": str(discount.id),
            "code": discount.code,
            "discount_type": discount.discount_type,
            "discount_value": discount.discount_value,
            "discount_amount": discount_amount,
            "max_discount": discount.max_discount,
            "message": f"Áp dụng mã giảm giá thành công! Giảm {int(discount_amount):,}đ"
        }

    def use_discount(self, code: str, session: Session) -> None:
        """Tăng số lần sử dụng sau khi checkout thành công"""
        discount = self.repository.get_by_code(code.upper(), session)
        if discount:
            self.repository.increment_used_count(discount, session)
