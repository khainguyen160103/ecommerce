"""
Order Router - API endpoints quản lý đơn hàng
Admin: Quản lý tất cả đơn hàng
User: CRUD đơn hàng cá nhân
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from uuid import UUID
from pydantic import BaseModel
from app.core.database import get_session
from app.models.order_model import OrderOut
from app.models.user_model import User
from app.services.order_service import OrderService
from app.deps.auth_dependency import get_current_user
from typing import Dict, Any, List, Annotated

orderRouter = APIRouter(prefix="/orders", tags=["Orders"])


class UpdateOrderStatusRequest(BaseModel):
    """Schema cập nhật trạng thái đơn hàng"""
    status: str


# ==================== USER ENDPOINTS ====================
@orderRouter.get("/my-orders", summary="[USER] Lấy danh sách đơn hàng của tôi")
def get_my_orders(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[OrderService, Depends()],
    skip: int = 0,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """
    [USER] Lấy danh sách đơn hàng của user hiện tại
    - Yêu cầu đăng nhập
    """
    return service.get_my_orders(
        user=current_user, session=session, skip=skip, limit=limit
    )


@orderRouter.get("/my-orders/{order_id}", summary="[USER] Xem chi tiết đơn hàng của tôi")
def get_my_order_by_id(
    order_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[OrderService, Depends()],
) -> Dict[str, Any]:
    """
    [USER] Xem chi tiết một đơn hàng
    - Yêu cầu đăng nhập
    - Chỉ xem được đơn hàng của mình
    """
    return service.get_order_detail(
        user=current_user, order_id=order_id, session=session
    )


@orderRouter.post("/", summary="[USER] Đặt hàng từ giỏ hàng")
def create_order_from_cart(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[OrderService, Depends()],
) -> Dict[str, Any]:
    """
    [USER] Tạo đơn hàng từ giỏ hàng
    - Yêu cầu đăng nhập
    - Chuyển toàn bộ sản phẩm trong giỏ thành đơn hàng
    - Giỏ hàng sẽ được xóa sau khi đặt hàng
    """
    return service.create_order_from_cart(user=current_user, session=session)


@orderRouter.post("/my-orders/{order_id}/cancel", summary="[USER] Hủy đơn hàng")
def cancel_my_order(
    order_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[OrderService, Depends()],
) -> Dict[str, str]:
    """
    [USER] Hủy đơn hàng
    - Yêu cầu đăng nhập
    - Chỉ hủy được đơn hàng đang ở trạng thái "pending"
    """
    return service.cancel_order(user=current_user, order_id=order_id, session=session)


# ==================== ADMIN ENDPOINTS ====================

@orderRouter.get("/", summary="[ADMIN] Lấy tất cả đơn hàng")
def get_all_orders(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[OrderService, Depends()],
    skip: int = 0,
    limit: int = 100,
    status_filter: Annotated[
        str | None, Query(description="Lọc theo trạng thái")
    ] = None,
) -> Dict[str, Any]:
    """
    [ADMIN] Lấy danh sách tất cả đơn hàng
    - Yêu cầu quyền Admin
    - Có thể lọc theo trạng thái
    """
    return service.get_all_orders(
        session=session,
        skip=skip,
        limit=limit,
        status_filter=status_filter
    )


@orderRouter.get("/{order_id}", summary="[ADMIN] Xem chi tiết đơn hàng")
def get_order_by_id(
    order_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[OrderService, Depends()],
) -> Dict[str, Any]:
    """
    [ADMIN] Xem chi tiết bất kỳ đơn hàng nào
    - Yêu cầu quyền Admin
    """
    return service.get_order_by_id(order_id=order_id, session=session)


@orderRouter.patch("/{order_id}/status", summary="[ADMIN] Cập nhật trạng thái đơn hàng")
def update_order_status(
    order_id: UUID,
    data: UpdateOrderStatusRequest,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[OrderService, Depends()],
) -> Dict[str, Any]:
    """
    [ADMIN] Cập nhật trạng thái đơn hàng
    - Yêu cầu quyền Admin
    - Các trạng thái: pending, confirmed, shipping, delivered, cancelled
    """
    return service.update_order_status(
        order_id=order_id,
        new_status=data.status,
        session=session
    )