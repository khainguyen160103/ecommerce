"""
Cart Router - API endpoints quản lý giỏ hàng
User: CRUD giỏ hàng cá nhân
Guest: Không có quyền (phải đăng nhập)
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session
from uuid import UUID
from pydantic import BaseModel
from app.core.database import get_session
from app.models.user_model import User
from app.services.cart_service import CartService
from app.deps.auth_dependency import get_current_user
from typing import Dict, Any, Optional

cartRouter = APIRouter(prefix="/cart", tags=["Cart"])


class AddToCartRequest(BaseModel):
    """Schema thêm sản phẩm vào giỏ"""

    cart_id: UUID
    product_id: UUID
    detail_id: UUID
    quantity: int = 1

class UpdateCartItemRequest(BaseModel):
    """Schema cập nhật số lượng"""
    quantity: int


# ==================== USER ENDPOINTS (Yêu cầu đăng nhập) ====================

@cartRouter.get("/", summary="[USER] Lấy giỏ hàng của tôi")
def get_my_cart(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    service: CartService = Depends()
) -> Dict[str, Any]:
    """
    [USER] Lấy thông tin giỏ hàng của user hiện tại
    - Yêu cầu đăng nhập
    - Tự động tạo giỏ hàng nếu chưa có
    """
    return service.get_my_cart(current_user=current_user, session=session)

# request
# user id
# product id
# detail

@cartRouter.post("/items", summary="[USER] Thêm sản phẩm vào giỏ")
def add_to_cart(
    data: AddToCartRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    service: CartService = Depends()
) -> Dict[str, Any]:
    """
    [USER] Thêm sản phẩm vào giỏ hàng
    - Yêu cầu đăng nhập
    - Nếu sản phẩm đã có trong giỏ, cộng thêm số lượng
    """
    print("data cart: ", data)
    return service.add_to_cart(
        current_user=current_user,
        product_id=data.product_id,
        quantity=data.quantity,
        detail_id=data.detail_id,
        session=session,
    )


@cartRouter.patch("/items/{cart_item_id}", summary="[USER] Cập nhật số lượng")
def update_cart_item(
    cart_item_id: UUID,
    data: UpdateCartItemRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    service: CartService = Depends()
) -> Dict[str, Any]:
    """
    [USER] Cập nhật số lượng sản phẩm trong giỏ
    - Yêu cầu đăng nhập
    - Nếu quantity <= 0, sản phẩm sẽ bị xóa khỏi giỏ
    """
    return service.update_cart_item(
        current_user=current_user,
        cart_item_id=cart_item_id,
        quantity=data.quantity,
        session=session
    )


@cartRouter.delete("/items/{cart_item_id}", summary="[USER] Xóa sản phẩm khỏi giỏ")
def remove_from_cart(
    cart_item_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    service: CartService = Depends()
) -> Dict[str, str]:
    """
    [USER] Xóa một sản phẩm khỏi giỏ hàng
    - Yêu cầu đăng nhập
    """
    return service.remove_from_cart(
        current_user=current_user,
        cart_item_id=cart_item_id,
        session=session
    )


@cartRouter.delete("/", summary="[USER] Xóa toàn bộ giỏ hàng")
def clear_cart(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    service: CartService = Depends()
) -> Dict[str, str]:
    """
    [USER] Xóa toàn bộ sản phẩm trong giỏ hàng
    - Yêu cầu đăng nhập
    """
    return service.clear_cart(current_user=current_user, session=session)