from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from app.utils.timezone import vn_now

if TYPE_CHECKING:
    from .user_model import User
    from .product_model import Product


class ReviewBase(SQLModel):
    product_id: UUID = Field(foreign_key="product.id", ondelete="CASCADE")
    user_id: UUID = Field(foreign_key="user.id", ondelete="CASCADE")
    rating: int = Field(ge=1, le=5)  # 1-5 sao
    comment: str | None = None


class ReviewIn(SQLModel):
    """Input schema - chỉ cần rating và comment"""
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class ReviewUpdate(SQLModel):
    """Update schema"""
    rating: int | None = Field(default=None, ge=1, le=5)
    comment: str | None = None


class ReviewOut(ReviewBase):
    id: UUID
    create_at: datetime
    update_at: datetime


class Review(ReviewBase, table=True):
    __tablename__ = 'review'
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    create_at: datetime = Field(default_factory=vn_now)
    update_at: datetime = Field(default_factory=vn_now)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="reviews")
    product: Optional["Product"] = Relationship(back_populates="reviews")
