from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID , uuid4
from datetime import datetime, timezone, timedelta
from typing import Optional

from .role_model import Role
from .adress_model import Address
from .cart_model import Cart
from .order_model import Order


VN_TIMEZONE = timezone(timedelta(hours=7))
class UserBase(SQLModel): 
    username : str
    email : str = Field(nullable=False, unique=True) 

class UserIn(UserBase): 
    password:str 

class UserOut(UserBase): 
    id : UUID 
    status: bool
    create_at: datetime
    update_at: datetime
    role: str | int | None
    

    
class User(UserBase, table = True): 
    __tablename__ = 'user'
    id : UUID = Field(default_factory=uuid4, primary_key=True)
    password_hashed : str
    status : bool = Field(default=True)
    create_at : datetime = Field(default_factory=datetime.now)
    update_at  : datetime = Field(default_factory=datetime.now)
    role_id : int | None = Field(default=1, foreign_key="role.id")
    # relationship 
    role : Optional['Role'] = Relationship(back_populates='user')
    cart : Optional['Cart'] = Relationship(back_populates='user')
    address: Optional["Address"] = Relationship(back_populates='user')
    order: Optional["Order"] = Relationship(back_populates='user')