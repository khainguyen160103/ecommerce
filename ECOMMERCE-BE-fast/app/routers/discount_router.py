"""
Discount Router - API endpoints cho mã giảm giá
Admin: CRUD mã giảm giá
User: Áp dụng mã giảm giá
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session
from pydantic import BaseModel
from app.core.database import get_session
from app.models.user_model import User
from app.models.discount_model import DiscountIn, DiscountUpdate, DiscountOut
from app.services.discount_service import DiscountService
from app.deps.auth_dependency import get_current_user, admin_required
from typing import Dict, Any, Annotated, List
from uuid import UUID

discountRouter = APIRouter(prefix="/discounts", tags=["Discounts"])


class ApplyDiscountRequest(BaseModel):
    """Schema áp dụng mã giảm giá"""
    code: str
    subtotal: float


# ==================== ADMIN ====================

@discountRouter.get("/", summary="[ADMIN] Lấy tất cả mã giảm giá", dependencies=[Depends(admin_required)])
def get_all_discounts(
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[DiscountService, Depends()],
) -> List[DiscountOut]:
    return service.get_all_discounts(session)


@discountRouter.get("/{discount_id}", summary="[ADMIN] Lấy mã giảm giá theo ID", dependencies=[Depends(admin_required)])
def get_discount_by_id(
    discount_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[DiscountService, Depends()],
) -> DiscountOut:
    return service.get_discount_by_id(discount_id, session)


@discountRouter.post("/", summary="[ADMIN] Tạo mã giảm giá", dependencies=[Depends(admin_required)])
def create_discount(
    data: DiscountIn,
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[DiscountService, Depends()],
) -> Dict[str, Any]:
    return service.create_discount(data, session)


@discountRouter.put("/{discount_id}", summary="[ADMIN] Cập nhật mã giảm giá", dependencies=[Depends(admin_required)])
def update_discount(
    discount_id: UUID,
    data: DiscountUpdate,
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[DiscountService, Depends()],
) -> Dict[str, Any]:
    return service.update_discount(discount_id, data, session)


@discountRouter.delete("/{discount_id}", summary="[ADMIN] Xóa mã giảm giá", dependencies=[Depends(admin_required)])
def delete_discount(
    discount_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[DiscountService, Depends()],
) -> Dict[str, str]:
    return service.delete_discount(discount_id, session)


# ==================== USER ====================

@discountRouter.post("/apply", summary="[USER] Áp dụng mã giảm giá")
def apply_discount(
    data: ApplyDiscountRequest,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[DiscountService, Depends()],
) -> Dict[str, Any]:
    return service.apply_discount(data.code, data.subtotal, session)
