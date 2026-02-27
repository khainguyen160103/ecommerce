"""
Address Repository - Xử lý tất cả query liên quan đến địa chỉ
"""
from sqlmodel import Session, select
from typing import List
from uuid import UUID

from app.models.adress_model import Address


class AddressRepository:
    """Repository quản lý địa chỉ giao hàng"""
    
    def get_address_by_id(self, address_id: UUID, session: Session) -> Address | None:
        """Lấy địa chỉ theo ID"""
        return session.exec(
            select(Address).where(Address.id == address_id)
        ).first()
    
    def get_addresses_by_user_id(
        self, 
        user_id: UUID, 
        session: Session
    ) -> List[Address]:
        """Lấy tất cả địa chỉ của user"""
        return session.exec(
            select(Address).where(Address.user_id == user_id)
        ).all()
    
    def create_address(self, address: Address, session: Session) -> Address:
        """Tạo địa chỉ mới"""
        session.add(address)
        session.commit()
        session.refresh(address)
        return address
    
    def update_address(self, address: Address, session: Session) -> Address:
        """Cập nhật địa chỉ - address đã tracked bởi session, không cần add lại"""
        session.commit()
        session.refresh(address)
        return address
    
    def delete_address(self, address: Address, session: Session) -> None:
        """Xóa địa chỉ"""
        session.delete(address)
        session.commit()
    
    def get_address_by_user_and_id(
        self, 
        user_id: UUID, 
        address_id: UUID, 
        session: Session
    ) -> Address | None:
        """Lấy địa chỉ theo user_id và address_id"""
        return session.exec(
            select(Address).where(
                (Address.id == address_id) & 
                (Address.user_id == user_id)
            )
        ).first()
