"""
Auth Router - API endpoints cho authentication
Bao gồm: đăng ký, đăng nhập, đổi mật khẩu, lấy thông tin user hiện tại
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from pydantic import BaseModel, EmailStr
from app.config.database import get_session
from app.models.user_model import User, UserIn, UserOut
from app.services.auth_service import AuthService
from app.dependencies.auth_dependency import get_current_user
from typing import Dict, Any

authRouter = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    """Schema cho request đăng ký"""
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """Schema cho request đăng nhập"""
    email: EmailStr
    password: str


class ChangePasswordRequest(BaseModel):
    """Schema cho request đổi mật khẩu"""
    old_password: str
    new_password: str


class TokenResponse(BaseModel):
    """Schema cho response token"""
    access_token: str
    token_type: str = "bearer"


# ==================== PUBLIC ENDPOINTS (Guest) ====================

@authRouter.post("/register", summary="[GUEST] Đăng ký tài khoản mới")
def register(
    data: RegisterRequest,
    session: Session = Depends(get_session),
    service: AuthService = Depends()
) -> Dict[str, Any]:
    """
    [GUEST] Đăng ký tài khoản mới
    - **name**: Tên người dùng
    - **email**: Email (unique)
    - **password**: Mật khẩu (tối thiểu 6 ký tự)
    """
    user_data = UserIn(name=data.name, email=data.email, password=data.password)
    return service.register(data=user_data, session=session)


@authRouter.post("/login", summary="[GUEST] Đăng nhập")
def login(
    data: LoginRequest,
    session: Session = Depends(get_session),
    service: AuthService = Depends()
) -> TokenResponse:
    """
    [GUEST] Đăng nhập và nhận JWT token
    - **email**: Email đã đăng ký
    - **password**: Mật khẩu
    
    Returns:
        access_token: JWT token để xác thực các request tiếp theo
    """
    user_data = UserIn(email=data.email, password=data.password, name="")
    token = service.login(data=user_data, session=session)
    return TokenResponse(access_token=token)


# ==================== USER ENDPOINTS (Yêu cầu đăng nhập) ====================

@authRouter.get("/me", summary="[USER] Lấy thông tin tài khoản")
def get_me(
    current_user: User = Depends(get_current_user)
) -> UserOut:
    """
    [USER] Lấy thông tin user hiện tại
    - Yêu cầu đăng nhập (Bearer token)
    """
    return UserOut.model_validate(current_user)


@authRouter.post("/change-password", summary="[USER] Đổi mật khẩu")
def change_password(
    data: ChangePasswordRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends()
) -> Dict[str, str]:
    """
    [USER] Đổi mật khẩu tài khoản
    - Yêu cầu đăng nhập
    - **old_password**: Mật khẩu hiện tại
    - **new_password**: Mật khẩu mới
    """
    return service.change_password(
        user=current_user,
        old_password=data.old_password,
        new_password=data.new_password,
        session=session
    )


@authRouter.post("/logout", summary="[USER] Đăng xuất")
def logout(
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    [USER] Đăng xuất
    - Yêu cầu đăng nhập
    - Client cần xóa token ở phía frontend
    
    Note: JWT là stateless, server không lưu token
    Để implement logout đầy đủ, cần thêm blacklist token (Redis)
    """
    return {"message": "Đăng xuất thành công"}

