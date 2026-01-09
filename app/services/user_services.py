"""
User Service - Xử lý logic quản lý người dùng
Admin: CRUD tất cả users
User: Xem và cập nhật thông tin cá nhân
"""
from app.models.user_model import User, UserOut
from app.utils.auth_helper import hash_password
from fastapi import HTTPException, status
from sqlmodel import Session, select
from uuid import UUID
from typing import List, Dict, Any


class UserService:
    """Service quản lý user"""
    
    # ==================== ADMIN FUNCTIONS ====================
    
    def get_all_users(self, session: Session, skip: int = 0, limit: int = 100) -> List[UserOut]:
        """
        [ADMIN] Lấy danh sách tất cả users
        Args:
            session: Database session
            skip: Số record bỏ qua (pagination)
            limit: Số record tối đa trả về
        Returns:
            List các UserOut
        """
        users = session.exec(select(User).offset(skip).limit(limit)).all()
        return [UserOut.model_validate(user) for user in users]
    
    def get_user_by_id(self, user_id: UUID, session: Session) -> UserOut:
        """
        [ADMIN] Lấy thông tin user theo ID
        Args:
            user_id: UUID của user
            session: Database session
        Returns:
            UserOut object
        Raises:
            HTTPException 404: User không tồn tại
        """
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User không tồn tại"
            )
        return UserOut.model_validate(user)
    
    def update_user_role(
        self, 
        user_id: UUID, 
        role_id: int, 
        session: Session
    ) -> Dict[str, Any]:
        """
        [ADMIN] Cập nhật role của user
        Args:
            user_id: UUID của user
            role_id: Role mới (0=Admin, 1=User)
            session: Database session
        Returns:
            Dict chứa message và user info
        """
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User không tồn tại"
            )
        
        user.role_id = role_id
        session.add(user)
        session.commit()
        session.refresh(user)
        
        return {
            "message": "Cập nhật role thành công",
            "user": UserOut.model_validate(user)
        }
    
    def toggle_user_status(self, user_id: UUID, session: Session) -> Dict[str, Any]:
        """
        [ADMIN] Kích hoạt/vô hiệu hóa tài khoản user
        Args:
            user_id: UUID của user
            session: Database session
        Returns:
            Dict chứa message và trạng thái mới
        """
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User không tồn tại"
            )
        
        user.status = not user.status
        session.add(user)
        session.commit()
        
        status_text = "kích hoạt" if user.status else "vô hiệu hóa"
        return {
            "message": f"Đã {status_text} tài khoản",
            "status": user.status
        }
    
    def delete_user(self, user_id: UUID, session: Session) -> Dict[str, str]:
        """
        [ADMIN] Xóa user (hard delete)
        Args:
            user_id: UUID của user
            session: Database session
        Returns:
            Dict chứa message
        """
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User không tồn tại"
            )
        
        session.delete(user)
        session.commit()
        
        return {"message": "Xóa user thành công"}
    
    # ==================== USER FUNCTIONS ====================
    
    def get_my_profile(self, current_user: User) -> UserOut:
        """
        [USER] Lấy thông tin cá nhân
        Args:
            current_user: User hiện tại
        Returns:
            UserOut object
        """
        return UserOut.model_validate(current_user)
    
    def update_my_profile(
        self, 
        current_user: User, 
        name: str | None,
        session: Session
    ) -> Dict[str, Any]:
        """
        [USER] Cập nhật thông tin cá nhân
        Args:
            current_user: User hiện tại
            name: Tên mới (optional)
            session: Database session
        Returns:
            Dict chứa message và user info
        """
        if name:
            current_user.name = name
        
        session.add(current_user)
        session.commit()
        session.refresh(current_user)
        
        return {
            "message": "Cập nhật thông tin thành công",
            "user": UserOut.model_validate(current_user)
        }
