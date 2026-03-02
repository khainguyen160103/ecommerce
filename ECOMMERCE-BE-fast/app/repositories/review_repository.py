from sqlmodel import Session, select, func
from sqlalchemy.orm import selectinload
from app.models.review_model import Review
from uuid import UUID
from typing import List, Dict, Any


class ReviewRepository:
    def get_by_product(
        self, product_id: UUID, session: Session, page: int = 1, limit: int = 20
    ) -> List[Review]:
        """Lấy danh sách đánh giá theo sản phẩm"""
        offset = (page - 1) * limit
        stmt = (
            select(Review)
            .where(Review.product_id == product_id)
            .options(selectinload(Review.user))
            .order_by(Review.create_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return session.exec(stmt).all()

    def count_by_product(self, product_id: UUID, session: Session) -> int:
        """Đếm tổng số đánh giá của sản phẩm"""
        stmt = select(func.count()).select_from(Review).where(Review.product_id == product_id)
        return session.exec(stmt).one()

    def get_avg_rating(self, product_id: UUID, session: Session) -> float:
        """Tính điểm đánh giá trung bình"""
        stmt = select(func.avg(Review.rating)).where(Review.product_id == product_id)
        result = session.exec(stmt).one()
        return round(float(result), 1) if result else 0.0

    def get_rating_distribution(self, product_id: UUID, session: Session) -> Dict[int, int]:
        """Phân bố số sao (1-5)"""
        stmt = (
            select(Review.rating, func.count())
            .where(Review.product_id == product_id)
            .group_by(Review.rating)
        )
        results = session.exec(stmt).all()
        distribution = {i: 0 for i in range(1, 6)}
        for rating, count in results:
            distribution[rating] = count
        return distribution

    def get_by_id(self, review_id: UUID, session: Session) -> Review | None:
        """Lấy đánh giá theo ID"""
        return session.exec(select(Review).where(Review.id == review_id)).first()

    def get_user_review(
        self, user_id: UUID, product_id: UUID, session: Session
    ) -> Review | None:
        """Kiểm tra user đã đánh giá sản phẩm chưa"""
        stmt = select(Review).where(
            Review.user_id == user_id, Review.product_id == product_id
        )
        return session.exec(stmt).first()

    def create(self, review: Review, session: Session) -> Review:
        """Tạo đánh giá mới"""
        session.add(review)
        session.commit()
        session.refresh(review)
        return review

    def update(self, review: Review, session: Session) -> Review:
        """Cập nhật đánh giá"""
        session.add(review)
        session.commit()
        session.refresh(review)
        return review

    def delete(self, review: Review, session: Session) -> None:
        """Xóa đánh giá"""
        session.delete(review)
        session.commit()
