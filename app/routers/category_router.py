"""
Category Router - API endpoints quản lý danh mục sản phẩm
Admin: CRUD categories
User/Guest: Xem danh mục
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session
from uuid import UUID
from app.config.database import get_session
from app.models.category_model import CategoryIn, CategoryOut
from app.models.user_model import User
from app.services.category_service import CategoryService
from app.dependencies.auth_dependency import admin_required
from typing import Dict, Any, List

categoryRouter = APIRouter(prefix="/categories", tags=["Categories"])


# ==================== PUBLIC ENDPOINTS (Guest có thể xem) ====================

@categoryRouter.get("/", summary="[PUBLIC] Lấy danh sách danh mục")
def get_all_categories(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    service: CategoryService = Depends()
) -> List[CategoryOut]:
    """
    [PUBLIC] Lấy danh sách tất cả danh mục sản phẩm
    - Không cần đăng nhập
    - **skip**: Số record bỏ qua
    - **limit**: Số record tối đa trả về
    """
    return service.get_all_categories(session=session, skip=skip, limit=limit)


@categoryRouter.get("/{category_id}", summary="[PUBLIC] Lấy chi tiết danh mục")
def get_category_by_id(
    category_id: UUID,
    session: Session = Depends(get_session),
    service: CategoryService = Depends()
) -> CategoryOut:
    """
    [PUBLIC] Lấy thông tin chi tiết của một danh mục
    - Không cần đăng nhập
    """
    return service.get_category_by_id(category_id=category_id, session=session)


# ==================== ADMIN ENDPOINTS ====================

@categoryRouter.post("/", summary="[ADMIN] Tạo danh mục mới")
def create_category(
    data: CategoryIn,
    session: Session = Depends(get_session),
    current_user: User = Depends(admin_required),
    service: CategoryService = Depends()
) -> Dict[str, Any]:
    """
    [ADMIN] Tạo danh mục sản phẩm mới
    - Yêu cầu quyền Admin
    """
    return service.create_category(data=data, session=session)


@categoryRouter.put("/{category_id}", summary="[ADMIN] Cập nhật danh mục")
def update_category(
    category_id: UUID,
    data: CategoryIn,
    session: Session = Depends(get_session),
    current_user: User = Depends(admin_required),
    service: CategoryService = Depends()
) -> Dict[str, Any]:
    """
    [ADMIN] Cập nhật thông tin danh mục
    - Yêu cầu quyền Admin
    """
    return service.update_category(
        category_id=category_id, 
        data=data, 
        session=session
    )


@categoryRouter.delete("/{category_id}", summary="[ADMIN] Xóa danh mục")
def delete_category(
    category_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(admin_required),
    service: CategoryService = Depends()
) -> Dict[str, str]:
    """
    [ADMIN] Xóa danh mục
    - Yêu cầu quyền Admin
    - Không thể xóa nếu còn sản phẩm trong danh mục
    """
    return service.delete_category(category_id=category_id, session=session)