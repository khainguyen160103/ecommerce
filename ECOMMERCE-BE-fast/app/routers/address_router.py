"""
Address Router - API endpoints quản lý địa chỉ giao hàng
User: CRUD địa chỉ cá nhân
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session
from uuid import UUID
from pydantic import BaseModel
from app.core.database import get_session
from app.models.adress_model import AddressIn, AddressOut
from app.models.user_model import User
from app.services.address_service import AddressService
from app.deps.auth_dependency import get_current_user
from typing import Dict, Any, List

addressRouter = APIRouter(prefix="/addresses", tags=["Addresses"])


class UpdateAddressRequest(BaseModel):
    """Schema cập nhật địa chỉ"""
    title: str | None = None
    address: str | None = None
    phone_number: str | None = None


# ==================== USER ENDPOINTS (Yêu cầu đăng nhập) ====================

@addressRouter.get("/", summary="[USER] Lấy danh sách địa chỉ của tôi")
def get_my_addresses(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    service: AddressService = Depends()
) -> List[AddressOut]:
    """
    [USER] Lấy danh sách địa chỉ giao hàng của user hiện tại
    - Yêu cầu đăng nhập
    """
    return service.get_my_addresses(user=current_user, session=session)


@addressRouter.get("/{address_id}", summary="[USER] Lấy chi tiết địa chỉ")
def get_address_by_id(
    address_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    service: AddressService = Depends()
) -> AddressOut:
    """
    [USER] Lấy chi tiết một địa chỉ
    - Yêu cầu đăng nhập
    - Chỉ xem được địa chỉ của mình
    """
    return service.get_address_by_id(
        user=current_user,
        address_id=address_id,
        session=session
    )


@addressRouter.post("/", summary="[USER] Thêm địa chỉ mới")
def create_address(
    data: AddressIn,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    service: AddressService = Depends()
) -> Dict[str, Any]:
    """
    [USER] Thêm địa chỉ giao hàng mới
    - Yêu cầu đăng nhập
    - **title**: Tiêu đề địa chỉ (VD: "Nhà", "Công ty")
    - **address**: Địa chỉ chi tiết
    - **phone_number**: Số điện thoại liên hệ
    """
    return service.create_address(
        user=current_user,
        data=data,
        session=session
    )


@addressRouter.put("/{address_id}", summary="[USER] Cập nhật địa chỉ")
def update_address(
    address_id: UUID,
    data: AddressIn,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    service: AddressService = Depends()
) -> Dict[str, Any]:
    """
    [USER] Cập nhật địa chỉ giao hàng
    - Yêu cầu đăng nhập
    - Chỉ cập nhật được địa chỉ của mình
    """
    return service.update_address(
        user=current_user,
        address_id=address_id,
        data=data,
        session=session
    )


@addressRouter.delete("/{address_id}", summary="[USER] Xóa địa chỉ")
def delete_address(
    address_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    service: AddressService = Depends()
) -> Dict[str, str]:
    """
    [USER] Xóa địa chỉ giao hàng
    - Yêu cầu đăng nhập
    - Chỉ xóa được địa chỉ của mình
    """
    return service.delete_address(
        user=current_user,
        address_id=address_id,
        session=session
    )
