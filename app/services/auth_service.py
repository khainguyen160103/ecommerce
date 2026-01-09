"""
Auth Service - Xử lý logic xác thực người dùng
Bao gồm: đăng ký, đăng nhập, đổi mật khẩu
"""
from app.utils.auth_helper import hash_password, verify_password
from app.models.user_model import User, UserIn, UserOut
from app.config.settings import settings
from app.utils.jwt_helper import create_access_token
from fastapi import HTTPException, status
from sqlmodel import Session, select
from datetime import timedelta
from typing import Dict, Any


class AuthService:
    """Service xử lý authentication"""
    
    def register(self, data: UserIn, session: Session) -> Dict[str, Any]:
        """
        Đăng ký user mới
        Args:
            data: Thông tin đăng ký (email, name, password)
            session: Database session
        Returns:
            Dict chứa thông tin user và message
        Raises:
            HTTPException 400: Email đã tồn tại
        """
        # Kiểm tra email đã tồn tại chưa
        existing_user = session.exec(
            select(User).where(User.email == data.email)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được sử dụng"
            )
        
        # Hash password và tạo user mới
        hashed_password = hash_password(data.password)
        user = User(
            email=data.email,
            name=data.name,
            password=hashed_password,
            role_id=1  # Mặc định là User role
        )
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        return {
            "message": "Đăng ký thành công",
            "user": UserOut.model_validate(user)
        }
    
    def login(self, data: UserIn, session: Session) -> Dict[str, Any]:
        """
        Đăng nhập và tạo JWT token
        Args:
            data: Thông tin đăng nhập (email, password)
            session: Database session
        Returns:
            Dict chứa access_token và user info
        Raises:
            HTTPException 401: Sai email hoặc password
        """
        # Tìm user theo email
        user = session.exec(
            select(User).where(User.email == data.email)
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email hoặc mật khẩu không đúng"
            )
        
        # Verify password
        if not verify_password(data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email hoặc mật khẩu không đúng"
            )
        
        # Kiểm tra trạng thái tài khoản
        if not user.status:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản đã bị vô hiệu hóa"
            )
        
        # Tạo access token
        token_data = {
            "user_id": str(user.id),
            "email": user.email,
            "role_id": user.role_id
        }
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(hours=24)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserOut.model_validate(user)
        }
    
    def change_password(
        self, 
        user: User, 
        old_password: str, 
        new_password: str, 
        session: Session
    ) -> Dict[str, str]:
        """
        Đổi mật khẩu user
        Args:
            user: User object hiện tại
            old_password: Mật khẩu cũ
            new_password: Mật khẩu mới
            session: Database session
        Returns:
            Dict chứa message thành công
        Raises:
            HTTPException 401: Mật khẩu cũ không đúng
        """
        if not verify_password(old_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Mật khẩu cũ không đúng"
            )
        
        user.password = hash_password(new_password)
        session.add(user)
        session.commit()
        
        return {"message": "Đổi mật khẩu thành công"}