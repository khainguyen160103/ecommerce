from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .product_model import Product
class CategoryBase(SQLModel):
    name: str = Field(nullable=False, unique=True)
    description: str | None = None

class CategoryIn(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: UUID
    create_at: datetime
    update_at: datetime

class Category(CategoryBase, table=True):
    __tablename__ = 'category'
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    create_at: datetime = Field(default_factory=datetime.now)
    update_at: datetime = Field(default_factory=datetime.now)
    
    # Relationship
    products: list["Product"] = Relationship(back_populates="category")