"""
Product Router - API endpoints quản lý sản phẩm
Admin: CRUD products
User/Guest: Xem sản phẩm
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from uuid import UUID
from app.config.database import get_session
from app.models.product_model import ProductIn, ProductOut
from app.models.user_model import User
from app.services.product_service import ProductService
from app.dependencies.auth_dependency import admin_required
from typing import Dict, Any, List

productRouter = APIRouter(prefix="/products", tags=["Products"])


# ==================== PUBLIC ENDPOINTS (Guest có thể xem) ====================

@productRouter.get("/", summary="[PUBLIC] Lấy danh sách sản phẩm")
def get_all_products(
    skip: int = 0,
    limit: int = 100,
    category_id: UUID | None = None,
    session: Session = Depends(get_session),
    service: ProductService = Depends()
) -> List[ProductOut]:
    """
    [PUBLIC] Lấy danh sách sản phẩm
    - Không cần đăng nhập
    - **skip**: Số record bỏ qua
    - **limit**: Số record tối đa trả về
    - **category_id**: Lọc theo danh mục (optional)
    """
    return service.get_all_products(
        session=session, 
        skip=skip, 
        limit=limit, 
        category_id=category_id
    )


@productRouter.get("/search", summary="[PUBLIC] Tìm kiếm sản phẩm")
def search_products(
    keyword: str = Query(..., description="Từ khóa tìm kiếm"),
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    service: ProductService = Depends()
) -> List[ProductOut]:
    """
    [PUBLIC] Tìm kiếm sản phẩm theo tên hoặc mô tả
    - Không cần đăng nhập
    """
    return service.search_products(
        keyword=keyword, 
        session=session, 
        skip=skip, 
        limit=limit
    )


@productRouter.get("/{product_id}", summary="[PUBLIC] Lấy chi tiết sản phẩm")
def get_product_by_id(
    product_id: UUID,
    session: Session = Depends(get_session),
    service: ProductService = Depends()
) -> ProductOut:
    """
    [PUBLIC] Lấy thông tin chi tiết sản phẩm
    - Không cần đăng nhập
    """
    return service.get_product_by_id(product_id=product_id, session=session)


# ==================== ADMIN ENDPOINTS ====================

@productRouter.post("/", summary="[ADMIN] Tạo sản phẩm mới")
def create_product(
    data: ProductIn,
    session: Session = Depends(get_session),
    current_user: User = Depends(admin_required),
    service: ProductService = Depends()
) -> Dict[str, Any]:
    """
    [ADMIN] Tạo sản phẩm mới
    - Yêu cầu quyền Admin
    """
    return service.create_product(data=data, session=session)


@productRouter.put("/{product_id}", summary="[ADMIN] Cập nhật sản phẩm")
def update_product(
    product_id: UUID,
    data: ProductIn,
    session: Session = Depends(get_session),
    current_user: User = Depends(admin_required),
    service: ProductService = Depends()
) -> Dict[str, Any]:
    """
    [ADMIN] Cập nhật thông tin sản phẩm
    - Yêu cầu quyền Admin
    """
    return service.update_product(
        product_id=product_id, 
        data=data, 
        session=session
    )


@productRouter.delete("/{product_id}", summary="[ADMIN] Xóa sản phẩm")
def delete_product(
    product_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(admin_required),
    service: ProductService = Depends()
) -> Dict[str, str]:
    """
    [ADMIN] Xóa sản phẩm
    - Yêu cầu quyền Admin
    """
    return service.delete_product(product_id=product_id, session=session)