from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user_model import User
    from .cart_item_model import CartItem
class CartBase(SQLModel):
    user_id: UUID = Field(foreign_key="user.id", unique=True)
    total: int = 0

class CartIn(CartBase):
    pass

class CartOut(CartBase):
    id: UUID
    create_at: datetime
    update_at: datetime

class Cart(CartBase, table=True):
    __tablename__ = 'cart'
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    create_at: datetime = Field(default_factory=datetime.now)
    update_at: datetime = Field(default_factory=datetime.now)
    
    # Relationship
    cart_items: list["CartItem"] = Relationship(back_populates="cart")
    user: "User" = Relationship(back_populates="cart")