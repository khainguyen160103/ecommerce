"""
User Service - Xử lý logic quản lý người dùng
Admin: CRUD tất cả users
User: Xem và cập nhật thông tin cá nhân
"""
from app.models.user_model import User, UserOut
from app.utils.auth_helper import hash_password
from app.repositories.user_repository import UserRepository
from fastapi import HTTPException, status, Depends
from sqlmodel import Session, select
from uuid import UUID
from typing import List, Dict, Any, Annotated
from app.utils.response_helper import ResponseHandler

class UserService:
    def __init__(self, repository: Annotated[UserRepository, Depends()]) -> None:
        self.repository = repository
    def get_user_by_email(self,session: Session, user_email:str) -> UserOut:
            user = self.repository.get_by_email(user_email,session)
            return user
    def get_all_users(self, session: Session, limit: int = 100, skip: int = 0,
         ) -> List[UserOut]:
        # công thức phân trang Offset = (page -1) * page size(LIMIT) 
        users = self.repository.get_all(session=session, skip=skip, limit=limit)
        return [UserOut.model_validate(user) for user in users]
    
    def get_user_by_id(self, user_id: UUID, session: Session) -> UserOut:
        user = self.repository.get_by_id(user_id, session=session)
        if not user:
            return ResponseHandler.error("Không tìm thấy người dùng", 404)
        return UserOut.model_validate(user)
    
    def update_user_role(
        self, 
        user_id: UUID, 
        role_id: int, 
        session: Session
    ) -> Dict[str, Any]:
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
        # user = session.exec(select(User).where(User.id == user_id)).first()
        user = self.repository.get_by_id(id=user_id, session=session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User không tồn tại"
            )
        
        
        
        return {"message": "Xóa user thành công"}
    
    # ==================== USER FUNCTIONS ====================
    
    def get_my_profile(self, current_user: User) -> UserOut:
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
