"""
GoShip Router - API endpoints cho dịch vụ vận chuyển GoShip
Bao gồm: Tỉnh/thành, Quận/huyện, Phường/xã, Tính phí, Tạo/Tracking đơn vận chuyển
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel
from app.core.database import get_session
from app.models.user_model import User
from app.deps.auth_dependency import get_current_user
from app.utils.goship import goship_client
from app.repositories.order_repository import OrderRepository
from app.repositories.address_repository import AddressRepository
from app.core.settings import settings
from typing import Dict, Any, Annotated, Optional
from uuid import UUID

goshipRouter = APIRouter(prefix="/goship", tags=["GoShip - Vận chuyển"])


class RateRequest(BaseModel):
    """Tính phí vận chuyển"""
    to_city: int
    to_district: int
    cod: int = 0
    amount: int = 0
    weight: int = 500


class CreateShipmentRequest(BaseModel):
    """Tạo đơn vận chuyển cho order"""
    order_id: str
    rate_id: str


# ==================== LOCATION ENDPOINTS ====================

@goshipRouter.get("/cities", summary="Lấy danh sách tỉnh/thành phố")
def get_cities() -> Dict[str, Any]:
    """Lấy danh sách tỉnh/thành phố từ GoShip"""
    try:
        cities = goship_client.get_cities()
        return {"data": cities}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Lỗi kết nối GoShip: {str(e)}"
        )


@goshipRouter.get("/cities/{city_id}/districts", summary="Lấy danh sách quận/huyện")
def get_districts(city_id: int) -> Dict[str, Any]:
    """Lấy danh sách quận/huyện theo tỉnh/thành"""
    try:
        districts = goship_client.get_districts(city_id)
        return {"data": districts}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Lỗi kết nối GoShip: {str(e)}"
        )


@goshipRouter.get("/districts/{district_id}/wards", summary="Lấy danh sách phường/xã")
def get_wards(district_id: int) -> Dict[str, Any]:
    """Lấy danh sách phường/xã theo quận/huyện"""
    try:
        wards = goship_client.get_wards(district_id)
        return {"data": wards}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Lỗi kết nối GoShip: {str(e)}"
        )


# ==================== RATE ENDPOINT ====================

@goshipRouter.post("/rates", summary="[USER] Tính phí vận chuyển")
def get_rates(
    data: RateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Dict[str, Any]:
    """
    Tính phí vận chuyển từ kho shop đến địa chỉ nhận
    Tự động dùng địa chỉ kho từ cấu hình GOSHIP_FROM_*
    Nếu GoShip không khả dụng, trả về phí mặc định
    """
    try:
        rates = goship_client.get_rates(
            from_city=settings.GOSHIP_FROM_CITY,
            from_district=settings.GOSHIP_FROM_DISTRICT,
            to_city=data.to_city,
            to_district=data.to_district,
            cod=data.cod,
            amount=data.amount,
            weight=data.weight,
        )
        return {"data": rates}
    except Exception as e:
        # Fallback rates khi GoShip sandbox không khả dụng
        fallback_rates = [
            {
                "id": "standard_fallback",
                "carrier_name": "Giao hàng tiêu chuẩn",
                "carrier_logo": "",
                "service": "Tiêu chuẩn",
                "fee": 30000,
                "estimated_pick_time": "1-2 ngày",
                "estimated_deliver_time": "3-5 ngày",
            },
            {
                "id": "express_fallback",
                "carrier_name": "Giao hàng nhanh",
                "carrier_logo": "",
                "service": "Nhanh",
                "fee": 50000,
                "estimated_pick_time": "Trong ngày",
                "estimated_deliver_time": "1-2 ngày",
            },
        ]
        return {"data": fallback_rates}


# ==================== SHIPMENT ENDPOINTS ====================

@goshipRouter.post("/shipments", summary="[ADMIN] Tạo đơn vận chuyển GoShip")
def create_shipment(
    data: CreateShipmentRequest,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    order_repo: Annotated[OrderRepository, Depends()],
    address_repo: Annotated[AddressRepository, Depends()],
) -> Dict[str, Any]:
    """
    [ADMIN] Tạo đơn vận chuyển trên GoShip cho một order
    - Lấy thông tin địa chỉ người nhận từ order
    - Dùng địa chỉ kho shop làm địa chỉ gửi
    """
    order_id = UUID(data.order_id)
    order = order_repo.get_order_by_id(order_id, session)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy đơn hàng"
        )

    if order.shipping_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Đơn hàng đã có mã vận chuyển: {order.shipping_code}"
        )

    # Lấy địa chỉ người nhận
    addresses = address_repo.get_addresses_by_user_id(order.user_id, session)
    if not addresses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Người nhận chưa có địa chỉ giao hàng"
        )
    addr = addresses[0]

    if not addr.city_id or not addr.district_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Địa chỉ người nhận chưa có thông tin tỉnh/quận để tạo đơn GoShip"
        )

    # Lấy user info
    user = order_repo.get_user_by_id(order.user_id, session)

    try:
        result = goship_client.create_shipment(
            rate_id=data.rate_id,
            from_name=settings.GOSHIP_FROM_NAME,
            from_phone=settings.GOSHIP_FROM_PHONE,
            from_street=settings.GOSHIP_FROM_STREET,
            from_ward=settings.GOSHIP_FROM_WARD,
            from_district=settings.GOSHIP_FROM_DISTRICT,
            from_city=settings.GOSHIP_FROM_CITY,
            to_name=user.username if user else addr.title or "Khách hàng",
            to_phone=addr.phone_number or "0000000000",
            to_street=addr.address,
            to_ward=addr.ward_id or 0,
            to_district=addr.district_id,
            to_city=addr.city_id,
            cod=order.total if not order.payment_id else 0,
            weight=500,
            metadata=f"Order {str(order.id)[:8]}",
        )

        # Lưu thông tin shipping vào order
        shipment_id = result.get("id") or result.get("shipment_id") or ""
        tracking = result.get("tracking_number") or result.get("code") or ""
        carrier_name = result.get("carrier") or result.get("carrier_name") or "GoShip"

        order.shipping_code = str(shipment_id)
        order.tracking_number = tracking
        order.carrier = carrier_name
        order.rate_id = data.rate_id
        order.status = "shipping"
        session.add(order)
        session.commit()

        return {
            "message": "Tạo đơn vận chuyển thành công",
            "order_id": str(order.id),
            "shipping_code": order.shipping_code,
            "tracking_number": order.tracking_number,
            "carrier": order.carrier,
            "goship_data": result,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Lỗi tạo đơn GoShip: {str(e)}"
        )


@goshipRouter.get("/shipments/{order_id}/tracking", summary="[USER/ADMIN] Tracking đơn vận chuyển")
def track_shipment(
    order_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    order_repo: Annotated[OrderRepository, Depends()],
) -> Dict[str, Any]:
    """Lấy thông tin tracking từ GoShip"""
    order = order_repo.get_order_by_id(UUID(order_id), session)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy đơn hàng"
        )

    if not order.shipping_code:
        return {
            "order_id": str(order.id),
            "status": order.status,
            "message": "Đơn hàng chưa được tạo vận chuyển trên GoShip",
            "tracking": None,
        }

    try:
        tracking_data = goship_client.get_shipment(order.shipping_code)
        return {
            "order_id": str(order.id),
            "status": order.status,
            "shipping_code": order.shipping_code,
            "tracking_number": order.tracking_number,
            "carrier": order.carrier,
            "tracking": tracking_data,
        }
    except Exception as e:
        return {
            "order_id": str(order.id),
            "status": order.status,
            "shipping_code": order.shipping_code,
            "tracking_number": order.tracking_number,
            "carrier": order.carrier,
            "tracking": None,
            "error": str(e),
        }


@goshipRouter.patch("/shipments/{order_id}/cancel", summary="[ADMIN] Hủy đơn vận chuyển")
def cancel_shipment(
    order_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    order_repo: Annotated[OrderRepository, Depends()],
) -> Dict[str, Any]:
    """[ADMIN] Hủy đơn vận chuyển trên GoShip"""
    order = order_repo.get_order_by_id(UUID(order_id), session)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy đơn hàng"
        )

    if not order.shipping_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Đơn hàng chưa có mã vận chuyển"
        )

    try:
        result = goship_client.cancel_shipment(order.shipping_code)
        order.status = "cancelled"
        session.add(order)
        session.commit()

        return {
            "message": "Đã hủy đơn vận chuyển",
            "order_id": str(order.id),
            "goship_data": result,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Lỗi hủy đơn GoShip: {str(e)}"
        )
