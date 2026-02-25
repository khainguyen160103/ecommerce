"""
Checkout Router - API endpoints cho quy trình thanh toán
Tích hợp VNPay QR và GoShip
"""
from fastapi import APIRouter, Depends, Request
from sqlmodel import Session
from pydantic import BaseModel
from app.core.database import get_session
from app.models.user_model import User
from app.services.checkout_service import CheckoutService
from app.deps.auth_dependency import get_current_user
from typing import Dict, Any, Annotated, Optional

checkoutRouter = APIRouter(prefix="/checkout", tags=["Checkout"])


class CheckoutRequest(BaseModel):
    """Schema tạo đơn hàng thanh toán"""
    payment_method: str  # "vnpay" hoặc "cod"
    address_id: Optional[str] = None
    shipping_method: str = "standard"  # "standard", "express"
    note: str = ""
    rate_id: Optional[str] = None  # GoShip rate ID
    shipping_fee: int = 0  # Phí vận chuyển


class ShippingRateRequest(BaseModel):
    """Schema tính phí vận chuyển"""
    address_id: str
    weight: float = 500  # gram
    

# ==================== CHECKOUT ENDPOINTS ====================

@checkoutRouter.post("/", summary="[USER] Tạo đơn hàng và thanh toán")
def create_checkout(
    data: CheckoutRequest,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[CheckoutService, Depends()],
) -> Dict[str, Any]:
    """
    [USER] Tạo đơn hàng từ giỏ hàng và xử lý thanh toán
    - payment_method: "vnpay" hoặc "cod"
    - Nếu VNPay: trả về payment_url để redirect
    - Nếu COD: tạo đơn hàng trực tiếp
    """
    # Lấy IP address của client
    client_ip = request.client.host if request.client else "127.0.0.1"
    
    return service.create_checkout(
        user=current_user,
        session=session,
        payment_method=data.payment_method,
        address_id=data.address_id,
        shipping_method=data.shipping_method,
        note=data.note,
        client_ip=client_ip,
        rate_id=data.rate_id,
        shipping_fee=data.shipping_fee,
    )


@checkoutRouter.get("/vnpay-return", summary="VNPay redirect callback")
def vnpay_return(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[CheckoutService, Depends()],
) -> Dict[str, Any]:
    """
    VNPay redirect user về URL này sau khi thanh toán
    FE sẽ đọc kết quả từ response
    """
    params = dict(request.query_params)
    return service.process_vnpay_return(params=params, session=session)


@checkoutRouter.get("/vnpay-ipn", summary="VNPay IPN callback")
def vnpay_ipn(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[CheckoutService, Depends()],
) -> Dict[str, str]:
    """
    VNPay server-to-server IPN callback
    Xác nhận thanh toán và cập nhật trạng thái
    """
    params = dict(request.query_params)
    return service.process_vnpay_ipn(params=params, session=session)


@checkoutRouter.post("/shipping-rates", summary="[USER] Tính phí vận chuyển")
def get_shipping_rates(
    data: ShippingRateRequest,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[CheckoutService, Depends()],
) -> Dict[str, Any]:
    """
    [USER] Tính phí vận chuyển qua GoShip
    - Trả về danh sách các phương thức vận chuyển và giá
    """
    return service.get_shipping_rates(
        user=current_user,
        session=session,
        address_id=data.address_id,
        weight=data.weight,
    )


@checkoutRouter.get("/order-preview", summary="[USER] Xem trước đơn hàng")
def get_order_preview(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[CheckoutService, Depends()],
) -> Dict[str, Any]:
    """
    [USER] Xem trước đơn hàng trước khi thanh toán
    - Trả về thông tin giỏ hàng, địa chỉ, tổng tiền
    """
    return service.get_order_preview(
        user=current_user,
        session=session,
    )
