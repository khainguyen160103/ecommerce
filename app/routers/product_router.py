"""
Product Router - API endpoints quản lý sản phẩm
Admin: CRUD products
User/Guest: Xem sản phẩm
"""
from fastapi import APIRouter, Depends, Query, Form, File, UploadFile
from sqlmodel import Session
from uuid import UUID
from typing import Annotated

from app.core.database import get_session
from app.deps.auth_dependency import admin_required
from app.models.product_model import ProductIn, ProductOut, ProductDetailOut, Product
from app.models.user_model import User
from app.services.product_service import ProductService
from app.models.product_detail_model import ProductDetailIn, ProductDetailOut
from sqlmodel import select
from app.models.product_detail_model import ProductDetail
from typing import Dict, Any, List

productRouter = APIRouter(prefix="/products", tags=["Products"])


# ==================== PUBLIC ENDPOINTS (Guest có thể xem) ====================

@productRouter.get("", summary="[PUBLIC] Lấy danh sách sản phẩm")
def get_all_products(
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[ProductService, Depends()],
    category_id: UUID | None = None,
    page: int = 0,
    limit: int = 20,
) -> Dict[str, Any]:
    # off set = (page -1 ) * pageSize(limit)
    # limit = pageSize
    return service.get_all_products(
        session=session, category_id=category_id, page=page, limit=limit
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
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[ProductService, Depends()],
) -> Dict[str, Any]:
    """
    [PUBLIC] Lấy thông tin chi tiết sản phẩm
    - Không cần đăng nhập
    """
    return service.get_product_by_id(product_id=product_id, session=session)


# ==================== ADMIN ENDPOINTS ====================

@productRouter.post("", dependencies=[Depends(admin_required)])
def create_product(
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[ProductService, Depends()],
    name: Annotated[str, Form()],
    description: Annotated[str, Form()],
    price: Annotated[str, Form()],
    category_id: Annotated[UUID, Form()],
    files: Annotated[List[UploadFile], File()],
) -> Dict[str, Any]:
    return service.create_product(
        name=name,
        description=description,
        price=price,
        category_id=category_id,
        files=files,
        session=session,
    )


@productRouter.put("/{product_id}", summary="[ADMIN] Cập nhật sản phẩm")
def update_product(
    product_id: UUID,
    data: ProductIn,
    session: Session = Depends(get_session),
    current_user: User = Depends(),
    service: ProductService = Depends(),
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


@productRouter.delete("/{product_id}", dependencies=[Depends(admin_required)])
def delete_product(
    product_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[ProductService, Depends()],
) -> Dict[str, str]:
    return service.delete_product(product_id=product_id, session=session)


@productRouter.post(
    "/{product_id}/details",
    summary="[ADMIN] Thêm chi tiết sản phẩm",
    dependencies=[Depends(admin_required)],
)
def add_product_detail(
    product_id: UUID,
    data: ProductDetailIn,
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[ProductService, Depends()],
) -> Dict[str, Any]:
    """
    [ADMIN] Thêm variant/chi tiết cho sản phẩm
    - Yêu cầu quyền Admin
    """
    return service.add_product_detail(product_id=product_id, data=data, session=session)


@productRouter.get(
    "/{product_id}/details", summary="[PUBLIC] Lấy danh sách chi tiết sản phẩm"
)
def get_product_details(
    product_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[ProductService, Depends()],
) -> Dict[str, Any]:
    """
    [PUBLIC] Lấy danh sách các variant/chi tiết của sản phẩm
    """

    return service.get_product_details(product_id=product_id, session=session)


@productRouter.put(
    "/{product_id}/details/{detail_id}",
    summary="[ADMIN] Cập nhật chi tiết sản phẩm",
    dependencies=[Depends(admin_required)],
)
def update_product_detail(
    product_id: UUID,
    detail_id: UUID,
    data: ProductDetailIn,
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[ProductService, Depends()],
) -> Dict[str, Any]:
    """
    [ADMIN] Cập nhật một variant/chi tiết của sản phẩm
    - Yêu cầu quyền Admin
    """
    return service.update_product_detail(
        product_id=product_id, detail_id=detail_id, data=data, session=session
    )


@productRouter.delete(
    "/{product_id}/details/{detail_id}",
    summary="[ADMIN] Xóa chi tiết sản phẩm",
    dependencies=[Depends(admin_required)],
)
def delete_product_detail(
    product_id: UUID,
    detail_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[ProductService, Depends()],
) -> Dict[str, str]:
    """
    [ADMIN] Xóa một variant/chi tiết của sản phẩm
    - Yêu cầu quyền Admin
    """
    return service.delete_product_detail(
        product_id=product_id, detail_id=detail_id, session=session
    )