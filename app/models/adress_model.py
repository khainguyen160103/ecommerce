from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4
from datetime import datetime

class AddressBase(SQLModel):
    user_id: UUID = Field(foreign_key="user.id")
    title: str | None = None
    address: str
    phone_number: str | None = None

class AddressIn(AddressBase):
    pass

class AddressOut(AddressBase):
    id: UUID
    create_at: datetime
    update_at: datetime

class Address(AddressBase, table=True):
    __tablename__ = 'address'
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    create_at: datetime = Field(default_factory=datetime.now)
    update_at: datetime = Field(default_factory=datetime.now)