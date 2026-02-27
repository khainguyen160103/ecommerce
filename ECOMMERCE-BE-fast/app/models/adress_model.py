from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user_model import User


# from app.models.user_model import User
class AddressBase(SQLModel):
    user_id: UUID = Field(foreign_key="user.id", unique=True)
    title: str | None = None
    address: str
    phone_number: str | None = None
    # GoShip location IDs
    city_id: int | None = Field(default=None)  # Tỉnh/Thành phố
    district_id: int | None = Field(default=None)  # Quận/Huyện
    ward_id: int | None = Field(default=None)  # Phường/Xã
    city_name: str | None = Field(default=None)
    district_name: str | None = Field(default=None)
    ward_name: str | None = Field(default=None)

class AddressIn(SQLModel):
    """Schema cho request tạo/cập nhật địa chỉ (không cần user_id)"""

    title: str | None = None
    address: str
    phone_number: str | None = None
    city_id: int | None = None
    district_id: int | None = None
    ward_id: int | None = None
    city_name: str | None = None
    district_name: str | None = None
    ward_name: str | None = None

class AddressOut(AddressBase):
    id: UUID
    create_at: datetime
    update_at: datetime

class Address(AddressBase, table=True):
    __tablename__ = 'address'
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    create_at: datetime = Field(default_factory=datetime.now)
    update_at: datetime = Field(default_factory=datetime.now)
    user: "User" = Relationship(back_populates="address")