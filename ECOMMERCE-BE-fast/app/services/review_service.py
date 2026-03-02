"""
Review Service - Xử lý logic đánh giá sản phẩm
User: Tạo, sửa, xóa đánh giá cá nhân
Guest/Public: Xem đánh giá sản phẩm
Admin: Xóa bất kỳ đánh giá nào
"""
from fastapi import HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session
from uuid import UUID
from typing import Annotated, Dict, Any
import math

from app.models.review_model import Review, ReviewIn, ReviewUpdate
from app.repositories.review_repository import ReviewRepository
from app.utils.response_helper import ResponseHandler


class ReviewService:
    """Service quản lý đánh giá sản phẩm"""

    def __init__(self, repository: Annotated[ReviewRepository, Depends()]):
        self.repository = repository

    def get_reviews_by_product(
        self,
        product_id: UUID,
        session: Session,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """[PUBLIC] Lấy danh sách đánh giá theo sản phẩm"""
        reviews = self.repository.get_by_product(
            product_id=product_id, session=session, page=page, limit=limit
        )
        total = self.repository.count_by_product(product_id=product_id, session=session)
        avg_rating = self.repository.get_avg_rating(product_id=product_id, session=session)
        distribution = self.repository.get_rating_distribution(
            product_id=product_id, session=session
        )

        reviews_data = []
        for review in reviews:
            review_dict = review.model_dump()
            review_dict["username"] = review.user.username if review.user else "Ẩn danh"
            reviews_data.append(review_dict)

        response = {
            "data": reviews_data,
            "summary": {
                "avg_rating": avg_rating,
                "total_reviews": total,
                "distribution": distribution,
            },
            "pagination": {
                "page": page,
                "pageSize": limit,
                "total_item": total,
                "totalPages": math.ceil(total / limit) if limit > 0 else 0,
            },
        }
        return JSONResponse(jsonable_encoder(response), 200)

    def create_review(
        self,
        product_id: UUID,
        user_id: UUID,
        review_in: ReviewIn,
        session: Session,
    ) -> Dict[str, Any]:
        """[USER] Tạo đánh giá cho sản phẩm"""
        # Kiểm tra user đã đánh giá sản phẩm này chưa
        existing = self.repository.get_user_review(
            user_id=user_id, product_id=product_id, session=session
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bạn đã đánh giá sản phẩm này rồi",
            )

        review = Review(
            product_id=product_id,
            user_id=user_id,
            rating=review_in.rating,
            comment=review_in.comment,
        )
        created = self.repository.create(review=review, session=session)
        return JSONResponse(
            jsonable_encoder(
                ResponseHandler.success(
                    "Đánh giá thành công", created.model_dump(), 201
                )
            ),
            201,
        )

    def update_review(
        self,
        review_id: UUID,
        user_id: UUID,
        review_update: ReviewUpdate,
        session: Session,
    ) -> Dict[str, Any]:
        """[USER] Cập nhật đánh giá của mình"""
        review = self.repository.get_by_id(review_id=review_id, session=session)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Đánh giá không tồn tại",
            )
        if review.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền sửa đánh giá này",
            )

        if review_update.rating is not None:
            review.rating = review_update.rating
        if review_update.comment is not None:
            review.comment = review_update.comment

        from datetime import datetime
        review.update_at = datetime.now()

        updated = self.repository.update(review=review, session=session)
        return JSONResponse(
            jsonable_encoder(
                ResponseHandler.success(
                    "Cập nhật đánh giá thành công", updated.model_dump(), 200
                )
            ),
            200,
        )

    def delete_review(
        self,
        review_id: UUID,
        user_id: UUID,
        session: Session,
        is_admin: bool = False,
    ) -> Dict[str, Any]:
        """[USER/ADMIN] Xóa đánh giá"""
        review = self.repository.get_by_id(review_id=review_id, session=session)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Đánh giá không tồn tại",
            )
        # Admin có thể xóa bất kỳ, user chỉ xóa của mình
        if not is_admin and review.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền xóa đánh giá này",
            )

        self.repository.delete(review=review, session=session)
        return JSONResponse(
            jsonable_encoder(
                ResponseHandler.success("Xóa đánh giá thành công", None, 200)
            ),
            200,
        )

    def get_my_review(
        self,
        product_id: UUID,
        user_id: UUID,
        session: Session,
    ) -> Dict[str, Any]:
        """[USER] Lấy đánh giá của mình cho sản phẩm"""
        review = self.repository.get_user_review(
            user_id=user_id, product_id=product_id, session=session
        )
        if not review:
            return JSONResponse(
                jsonable_encoder({"data": None}), 200
            )
        return JSONResponse(
            jsonable_encoder({"data": review.model_dump()}), 200
        )
