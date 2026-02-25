from sqlmodel import SQLModel, Field, Relationship
from uuid import uuid4, UUID
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .product_model import Product

class ProductImage(SQLModel, table=True): 
    __tablename__= 'product_image' 
    id: UUID = Field(primary_key=True, default_factory= uuid4)
    product_id: UUID = Field(foreign_key='product.id',ondelete="CASCADE", nullable=False)

    # cloudinary info to delete image 
    cloudinary_public_id : str = Field(nullable=False, unique=True)
    url:str # ảnh full size 
    thumbnail_url:str = Field(nullable=False) # ảnh nhỏ nếu click vào sẽ hiển thị ảnh lớn 
    created_at:datetime = Field(default_factory=datetime.now)
    
    # Relationship
    product: "Product" = Relationship(back_populates="images"
                                      )