"""
Review Router - API endpoints đánh giá sản phẩm
Public: Xem đánh giá
User: Tạo, sửa, xóa đánh giá cá nhân
Admin: Xóa bất kỳ đánh giá
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from uuid import UUID
from typing import Annotated, Dict, Any

from app.core.database import get_session
from app.deps.auth_dependency import get_current_user, admin_required
from app.models.user_model import UserOut
from app.models.review_model import ReviewIn, ReviewUpdate
from app.services.review_service import ReviewService

reviewRouter = APIRouter(prefix="/reviews", tags=["Reviews"])


# ==================== PUBLIC ENDPOINTS ====================


@reviewRouter.get(
    "/product/{product_id}",
    summary="[PUBLIC] Lấy đánh giá theo sản phẩm",
)
def get_reviews_by_product(
    product_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[ReviewService, Depends()],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> Dict[str, Any]:
    """
    [PUBLIC] Lấy danh sách đánh giá của một sản phẩm
    - Không cần đăng nhập
    - Bao gồm: danh sách reviews, avg rating, phân bố sao
    """
    return service.get_reviews_by_product(
        product_id=product_id, session=session, page=page, limit=limit
    )


# ==================== USER ENDPOINTS ====================


@reviewRouter.post(
    "/product/{product_id}",
    summary="[USER] Tạo đánh giá cho sản phẩm",
)
def create_review(
    product_id: UUID,
    review_in: ReviewIn,
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[ReviewService, Depends()],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> Dict[str, Any]:
    """
    [USER] Đánh giá sản phẩm (1-5 sao + bình luận)
    - Mỗi user chỉ được đánh giá 1 lần cho mỗi sản phẩm
    """
    return service.create_review(
        product_id=product_id,
        user_id=current_user.id,
        review_in=review_in,
        session=session,
    )


@reviewRouter.get(
    "/my-review/{product_id}",
    summary="[USER] Lấy đánh giá của tôi cho sản phẩm",
)
def get_my_review(
    product_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[ReviewService, Depends()],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> Dict[str, Any]:
    """
    [USER] Kiểm tra xem tôi đã đánh giá sản phẩm này chưa
    """
    return service.get_my_review(
        product_id=product_id,
        user_id=current_user.id,
        session=session,
    )


@reviewRouter.put(
    "/{review_id}",
    summary="[USER] Cập nhật đánh giá",
)
def update_review(
    review_id: UUID,
    review_update: ReviewUpdate,
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[ReviewService, Depends()],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> Dict[str, Any]:
    """
    [USER] Cập nhật đánh giá của mình
    """
    return service.update_review(
        review_id=review_id,
        user_id=current_user.id,
        review_update=review_update,
        session=session,
    )


@reviewRouter.delete(
    "/{review_id}",
    summary="[USER] Xóa đánh giá của mình",
)
def delete_review(
    review_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[ReviewService, Depends()],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> Dict[str, Any]:
    """
    [USER] Xóa đánh giá của mình
    """
    return service.delete_review(
        review_id=review_id,
        user_id=current_user.id,
        session=session,
    )


# ==================== ADMIN ENDPOINTS ====================


@reviewRouter.delete(
    "/admin/{review_id}",
    summary="[ADMIN] Xóa bất kỳ đánh giá nào",
    dependencies=[Depends(admin_required)],
)
def admin_delete_review(
    review_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[ReviewService, Depends()],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> Dict[str, Any]:
    """
    [ADMIN] Xóa bất kỳ đánh giá nào (quản trị)
    """
    return service.delete_review(
        review_id=review_id,
        user_id=current_user.id,
        session=session,
        is_admin=True,
    )
