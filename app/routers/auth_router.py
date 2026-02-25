"""
Auth Router - API endpoints cho authentication
Bao gồm: đăng ký, đăng nhập, đổi mật khẩu, lấy thông tin user hiện tại, OAuth
"""

from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from typing import Dict, Any, Annotated

from app.core.database import get_session
from app.deps.auth_dependency import get_current_user, user_required, admin_required
from app.models.user_model import User, UserIn, UserOut
from app.services.auth_service import AuthService
from app.schemas.auth_schemas import (
    ResponseLogin,
    GoogleLoginSchema,
    FacebookLoginSchema,
    ChangePasswordSchema,
)

authRouter = APIRouter(prefix="/auth", tags=["Authentication"])


@authRouter.post("/register", summary="[Role = GUEST] Đăng ký tài khoản mới")
def register(
    data: UserIn,
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[AuthService, Depends()],
) -> dict[str, Any]:

    return service.register(data=data, session=session)


@authRouter.post("/token", summary="[GUEST] Đăng nhập")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[AuthService, Depends()],
    response: Response,
) -> Dict[str, Any]:
    return service.login(response=response, data=form_data, session=session)


@authRouter.get("/me")
def get_me(current_user: Annotated[UserOut, Depends(get_current_user)]) -> UserOut:
    return current_user


@authRouter.post("/change-password", summary="[USER] Đổi mật khẩu")
def change_password(
    data: ChangePasswordSchema,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
    service: Annotated[AuthService, Depends()],
) -> Dict[str, str]:
    return service.change_password(
        current_user=current_user,
        old_password=data.old_password,
        new_password=data.new_password,
        session=session,
    )


@authRouter.post("/logout", summary="[USER] Đăng xuất")
def logout(
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    return {"message": "Đăng xuất thành công"}


@authRouter.post("/google", summary="[GUEST] Đăng nhập bằng Google")
def google_login(
    data: GoogleLoginSchema,
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[AuthService, Depends()],
    response: Response,
) -> Dict[str, Any]:
    return service.google_login(data=data, response=response, session=session)


@authRouter.post("/facebook", summary="[GUEST] Đăng nhập bằng Facebook")
def facebook_login(
    data: FacebookLoginSchema,
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[AuthService, Depends()],
    response: Response,
) -> Dict[str, Any]:
    return service.facebook_login(data=data, response=response, session=session)

