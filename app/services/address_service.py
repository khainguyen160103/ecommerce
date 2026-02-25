"""
Address Service - Xử lý logic địa chỉ giao hàng
User: CRUD địa chỉ của mình
"""
from app.models.adress_model import Address, AddressIn, AddressOut
from app.models.user_model import User
from app.repositories.address_repository import AddressRepository
from fastapi import HTTPException, status
from sqlmodel import Session
from uuid import UUID
from typing import Dict, Any, List


class AddressService:
    """Service quản lý địa chỉ giao hàng"""

    def __init__(self):
        self.repository = AddressRepository()

    def get_my_addresses(self, user: User, session: Session) -> List[AddressOut]:
        """
        [USER] Lấy danh sách địa chỉ của user
        Args:
            user: User hiện tại
            session: Database session
        Returns:
            List các AddressOut
        """
        addresses = self.repository.get_addresses_by_user_id(user.id, session)

        return [AddressOut.model_validate(addr) for addr in addresses]

    def create_address(
        self, user: User, data: AddressIn, session: Session
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
        # Kiểm tra user đã có địa chỉ chưa (unique constraint trên user_id)
        existing = self.repository.get_addresses_by_user_id(user.id, session)
        if existing:
            # Cập nhật địa chỉ hiện có thay vì tạo mới
            address = existing[0]
            address.title = data.title
            address.address = data.address
            address.phone_number = data.phone_number
            address.city_id = data.city_id
            address.district_id = data.district_id
            address.ward_id = data.ward_id
            address.city_name = data.city_name
            address.district_name = data.district_name
            address.ward_name = data.ward_name
            address = self.repository.update_address(address, session)
            return {
                "message": "Cập nhật địa chỉ thành công",
                "address": AddressOut.model_validate(address),
            }

        address = Address(
            user_id=user.id,
            title=data.title,
            address=data.address,
            phone_number=data.phone_number,
            city_id=data.city_id,
            district_id=data.district_id,
            ward_id=data.ward_id,
            city_name=data.city_name,
            district_name=data.district_name,
            ward_name=data.ward_name,
        )

        address = self.repository.create_address(address, session)
        
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
        address = self.repository.get_address_by_user_and_id(
            user.id, address_id, session
        )
        
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Địa chỉ không tồn tại"
            )
        
        address.title = data.title
        address.address = data.address
        address.phone_number = data.phone_number
        address.city_id = data.city_id
        address.district_id = data.district_id
        address.ward_id = data.ward_id
        address.city_name = data.city_name
        address.district_name = data.district_name
        address.ward_name = data.ward_name

        address = self.repository.update_address(address, session)

        return {
            "message": "Cập nhật địa chỉ thành công",
            "address": AddressOut.model_validate(address),
        }

    def delete_address(
        self, user: User, address_id: UUID, session: Session
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
        address = self.repository.get_address_by_user_and_id(
            user.id, address_id, session
        )

        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Địa chỉ không tồn tại"
            )

        self.repository.delete_address(address, session)
        
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
        address = self.repository.get_address_by_user_and_id(
            user.id, address_id, session
        )
        
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Địa chỉ không tồn tại"
            )
        
        return AddressOut.model_validate(address)