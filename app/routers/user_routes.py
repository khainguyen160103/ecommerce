"""
User Router - API endpoints quản lý người dùng
Admin: CRUD users
User: Xem và cập nhật profile cá nhân
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session
from pydantic import BaseModel
from uuid import UUID
from app.config.database import get_session
from app.models.user_model import User, UserOut
from app.services.user_services import UserService
from app.dependencies.auth_dependency import (
    get_current_user, 
    admin_required, 
    user_required
)
from typing import Dict, Any, List

userRouter = APIRouter(prefix="/users", tags=["Users"])


class UpdateProfileRequest(BaseModel):
    """Schema cho cập nhật profile"""
    name: str | None = None


class UpdateRoleRequest(BaseModel):
    """Schema cho cập nhật role"""
    role_id: int


# ==================== ADMIN ENDPOINTS ====================

@userRouter.get("/", summary="[ADMIN] Lấy danh sách users")
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(admin_required),
    service: UserService = Depends()
) -> List[UserOut]:
    """
    [ADMIN] Lấy danh sách tất cả users với pagination
    - **skip**: Số record bỏ qua
    - **limit**: Số record tối đa trả về
    """
    return service.get_all_users(session=session, skip=skip, limit=limit)


@userRouter.get("/{user_id}", summary="[ADMIN] Lấy thông tin user")
def get_user_by_id(
    user_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(admin_required),
    service: UserService = Depends()
) -> UserOut:
    """
    [ADMIN] Lấy thông tin chi tiết của một user
    """
    return service.get_user_by_id(user_id=user_id, session=session)


@userRouter.patch("/{user_id}/role", summary="[ADMIN] Cập nhật role user")
def update_user_role(
    user_id: UUID,
    data: UpdateRoleRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(admin_required),
    service: UserService = Depends()
) -> Dict[str, Any]:
    """
    [ADMIN] Cập nhật role cho một user
    """
    return service.update_user_role(user_id=user_id, role_id=data.role_id, session=session)


# ==================== USER ENDPOINTS ====================

@userRouter.get("/me", summary="Lấy thông tin profile cá nhân")
def get_profile(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends()
) -> UserOut:
    """
    Lấy thông tin profile của người dùng hiện tại
    """
    return service.get_user_by_id(user_id=current_user.id)


@userRouter.patch("/me", summary="Cập nhật thông tin profile cá nhân")
def update_profile(
    data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends()
) -> UserOut:
    """
    Cập nhật thông tin profile của người dùng hiện tại
    """
    return service.update_user_profile(user_id=current_user.id, name=data.name)