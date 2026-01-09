from sqlmodel import Field, SQLModel, create_engine, Session, Relationship
from uuid import UUID , uuid4
from datetime import datetime, timezone, timedelta
VN_TIMEZONE = timezone(timedelta(hours=7))

from .role_model import Role

class UserBase(SQLModel): 
    name : str
    email : str = Field(nullable=False, unique=True)

class UserIn(UserBase): 
    password:str 

class UserOut(UserBase): 
    id : UUID 
    status: bool
    create_at: datetime
    update_at: datetime
    role_id: int | None
    
class User(UserBase, table = True): 
    __tablename__ = 'user'
    id : UUID = Field(default_factory=uuid4, primary_key=True)
    password_hashed : str
    status : bool = Field(default=True)
    create_at : datetime = Field(default_factory=datetime.now)
    update_at  : datetime = Field(default_factory=datetime.now)
    role_id : int | None = Field(default=1 , foreign_key="role.id")
    # relationship 
    role : Role | None = Relationship(back_populates='user')


# create engine to connect database , echo parameter set for appliation print sql statement in terminal 
# engine = create_engine(DATABASE_URL, echo=True)

# SQLModel.metadata.create_all(engine)