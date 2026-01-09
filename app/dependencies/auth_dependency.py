"""
Authentication & Authorization Dependencies
Xử lý xác thực và phân quyền cho các API endpoints
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from app.config.database import get_session
from app.models.user_model import User
from app.utils.jwt_helper import verify_token
from typing import List

# Sử dụng Bearer token authentication
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """
    Dependency: Lấy user hiện tại từ JWT token
    - Verify token
    - Trả về User object
    Raises:
        HTTPException 401: Token không hợp lệ hoặc user không tồn tại
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không chứa thông tin user"
        )
    
    user = session.exec(select(User).where(User.id == user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User không tồn tại"
        )
    
    if not user.status:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị vô hiệu hóa"
        )
    
    return user


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    session: Session = Depends(get_session)
) -> User | None:
    """
    Dependency: Lấy user hiện tại (optional - cho Guest)
    - Nếu có token hợp lệ -> trả về User
    - Nếu không có token -> trả về None (Guest)
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        return None
    
    user_id = payload.get("user_id")
    if user_id is None:
        return None
    
    user = session.exec(select(User).where(User.id == user_id)).first()
    return user


class RoleChecker:
    """
    Dependency class: Kiểm tra role của user
    Usage:
        @router.get("/admin-only", dependencies=[Depends(RoleChecker([0]))])
        def admin_endpoint():
            pass
    """
    def __init__(self, allowed_roles: List[int]):
        """
        Args:
            allowed_roles: Danh sách role_id được phép truy cập
                - 0: Admin
                - 1: User  
                - None/Guest: Không cần đăng nhập
        """
        self.allowed_roles = allowed_roles
    
    def __call__(self, user: User = Depends(get_current_user)) -> User:
        if user.role_id not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền truy cập chức năng này"
            )
        return user


def admin_required(user: User = Depends(RoleChecker([0]))) -> User:
    """Dependency: Yêu cầu quyền Admin (role_id = 0)"""
    return user

def user_required(user: User = Depends(RoleChecker([0, 1]))) -> User:
    """Dependency: Yêu cầu đăng nhập (Admin hoặc User)"""
    return user