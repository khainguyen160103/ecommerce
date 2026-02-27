"""
User Router - API endpoints quản lý người dùng
Admin: CRUD users
User: Xem và cập nhật profile cá nhân
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session
from pydantic import BaseModel
from uuid import UUID
from typing import Dict, Any, List, Annotated

from app.core.database import get_session
from app.deps.auth_dependency import user_required , admin_required
from app.models.user_model import User, UserOut
from app.services.user_services import UserService
from app.repositories.user_repository import UserRepository
from app.deps.auth_dependency import (
    get_current_user, 
)

userRouter = APIRouter(prefix="/users", tags=["Users"])


class UpdateProfileRequest(BaseModel):
    """Schema cho cập nhật profile"""
    name: str | None = None


class UpdateRoleRequest(BaseModel):
    """Schema cho cập nhật role"""
    role_id: int

@userRouter.get("/" ,dependencies=[Depends(admin_required)])
def get_all_users(
    session: Annotated[Session, Depends(get_session)], 
    service: Annotated[UserService, Depends()],
    skip: int = 0,
    limit: int = 100,
) -> List[UserOut]:
    """
    [ADMIN] Lấy danh sách tất cả users với pagination
    - **skip**: Số record bỏ qua
    - **limit**: Số record tối đa trả về
    """
    return service.get_all_users(session=session, skip=skip, limit=limit)


@userRouter.get("/{user_id}", dependencies=[Depends(admin_required)])
def get_user_by_id(
    user_id: UUID,
    session: Session = Depends(get_session),
    service: UserService = Depends()
) -> UserOut:
    """
    [ADMIN] Lấy thông tin chi tiết của một user
    """
    return service.get_user_by_id(user_id=user_id, session=session)


# @userRouter.patch("/{user_id}/role", summary="[ADMIN] Cập nhật role user")
# def update_user_role(
#     user_id: UUID,
#     data: UpdateRoleRequest,
#     session: Session = Depends(get_session),
#     current_user: User = Depends(),
#     service: UserService = Depends()
# ) -> Dict[str, Any]:
#     """
#     [ADMIN] Cập nhật role cho một user
#     """
#     return service.update_user_role(user_id=user_id, role_id=data.role_id, session=session)


# ==================== USER ENDPOINTS ====================

@userRouter.patch("/me",dependencies=[Depends(user_required)])
def update_profile(
    data: UpdateProfileRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[UserService, Depends()]
) -> UserOut:
    """
    Cập nhật thông tin profile của người dùng hiện tại
    """
    return service.update_user_profile(user_id=current_user.id, name=data.name)