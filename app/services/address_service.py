"""
Address Service - Xử lý logic địa chỉ giao hàng
User: CRUD địa chỉ của mình
"""
from app.models.adress_model import Address, AddressIn, AddressOut
from app.models.user_model import User
from fastapi import HTTPException, status
from sqlmodel import Session, select
from uuid import UUID
from typing import Dict, Any, List


class AddressService:
    """Service quản lý địa chỉ giao hàng"""
    
    def get_my_addresses(self, user: User, session: Session) -> List[AddressOut]:
        """
        [USER] Lấy danh sách địa chỉ của user
        Args:
            user: User hiện tại
            session: Database session
        Returns:
            List các AddressOut
        """
        addresses = session.exec(
            select(Address).where(Address.user_id == user.id)
        ).all()
        
        return [AddressOut.model_validate(addr) for addr in addresses]
    
    def create_address(
        self, 
        user: User, 
        data: AddressIn, 
        session: Session
    ) -> Dict[str, Any]:
        """
        [USER] Thêm địa chỉ mới
        Args:
            user: User hiện tại
            data: Thông tin địa chỉ
            session: Database session
        Returns:
            Dict chứa message và address info
        """
        address = Address(
            user_id=user.id,
            title=data.title,
            address=data.address,
            phone_number=data.phone_number
        )
        
        session.add(address)
        session.commit()
        session.refresh(address)
        
        return {
            "message": "Thêm địa chỉ thành công",
            "address": AddressOut.model_validate(address)
        }
    
    def update_address(
        self, 
        user: User, 
        address_id: UUID, 
        data: AddressIn, 
        session: Session
    ) -> Dict[str, Any]:
        """
        [USER] Cập nhật địa chỉ
        Args:
            user: User hiện tại
            address_id: UUID của địa chỉ
            data: Thông tin mới
            session: Database session
        Returns:
            Dict chứa message và address info
        """
        address = session.exec(
            select(Address).where(
                Address.id == address_id,
                Address.user_id == user.id
            )
        ).first()
        
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Địa chỉ không tồn tại"
            )
        
        address.title = data.title
        address.address = data.address
        address.phone_number = data.phone_number
        
        session.add(address)
        session.commit()
        session.refresh(address)
        
        return {
            "message": "Cập nhật địa chỉ thành công",
            "address": AddressOut.model_validate(address)
        }
    
    def delete_address(
        self, 
        user: User, 
        address_id: UUID, 
        session: Session
    ) -> Dict[str, str]:
        """
        [USER] Xóa địa chỉ
        Args:
            user: User hiện tại
            address_id: UUID của địa chỉ
            session: Database session
        Returns:
            Dict chứa message
        """
        address = session.exec(
            select(Address).where(
                Address.id == address_id,
                Address.user_id == user.id
            )
        ).first()
        
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Địa chỉ không tồn tại"
            )
        
        session.delete(address)
        session.commit()
        
        return {"message": "Xóa địa chỉ thành công"}
    
    def get_address_by_id(
        self, 
        user: User, 
        address_id: UUID, 
        session: Session
    ) -> AddressOut:
        """
        [USER] Lấy chi tiết địa chỉ theo ID
        Args:
            user: User hiện tại
            address_id: UUID của địa chỉ
            session: Database session
        Returns:
            AddressOut object
        Raises:
            HTTPException 404: Địa chỉ không tồn tại hoặc không thuộc user
        """
        address = session.exec(
            select(Address).where(
                Address.id == address_id,
                Address.user_id == user.id
            )
        ).first()
        
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Địa chỉ không tồn tại"
            )
        
        return AddressOut.model_validate(address)