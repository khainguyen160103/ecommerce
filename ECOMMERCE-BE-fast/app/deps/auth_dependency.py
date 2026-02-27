
from fastapi import Depends
from sqlmodel import Session
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated, List

from app.utils.jwt_helper import verify_token
from app.models.user_model import UserOut
from app.core.database import get_session
from app.services.user_services import UserService
from app.repositories.user_repository import UserRepository
from app.utils.response_helper import ResponseHandler

authSchemes = OAuth2PasswordBearer(
    tokenUrl='api/auth/token')

def get_current_user(
    token: Annotated[str,Depends(authSchemes)],
    service : Annotated[UserService , Depends()],
    session: Annotated[Session, Depends(get_session)],
) -> UserOut:
    print("token: " ,token)
    if not token: 
        return ResponseHandler.error("Vui Lòng đăng nhập để tiếp tục", 401)
    payload = verify_token(token=token)
    if not payload: 
        return ResponseHandler.error("You don't have permission to do that")
    print("Payload: ", payload)
    email = payload.get('email')
    if email is None: 
        return ResponseHandler.error("Something error on Server")
    user = service.get_user_by_email(session=session, user_email=email)
    if not user:
        return ResponseHandler.error("Please try again, something wrong error")
    return UserOut.model_validate(user)

def admin_required(current_user : Annotated[UserOut, Depends(get_current_user)]) -> any: 
    print("role user: " , current_user.role)
    if current_user.role != "ADMIN":
        return ResponseHandler.error("Bạn không có quyền gọi API này", 401)

def user_required(current_user : Annotated[UserOut, Depends(get_current_user)]) -> any: 
    if current_user.role != "USER": 
        return ResponseHandler.error("Vui đăng nhập để sử dụng tiếp các chức năng" ,401)