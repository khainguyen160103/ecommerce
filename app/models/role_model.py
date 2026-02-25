from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user_model import User
class Role(SQLModel, table=True): 
    '''
    role id = 1 (user), id = 0 admin
    '''
    __tablename__='role'
    id : int | None = Field(default=None, primary_key=True)
    description: str 
    # relationship 
    user : list["User"] = Relationship(back_populates='role')  