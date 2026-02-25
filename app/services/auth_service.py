"""
Auth Service - Xử lý logic xác thực người dùng
Bao gồm: đăng ký, đăng nhập, đổi mật khẩu, OAuth Google/Facebook
"""

from fastapi import HTTPException, Response, status, Depends
from sqlmodel import Session
from typing import Dict, Any, Annotated
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timezone
import httpx
import jwt as pyjwt
from uuid import uuid4
from app.utils.auth_helper import hash_password, verify_password
from app.utils.jwt_helper import create_access_token, create_refresh_token
from app.models.user_model import User, UserIn, UserOut
from app.schemas.auth_schemas import (
    ResponseLogin,
    GoogleLoginSchema,
    FacebookLoginSchema,
)
from app.repositories.user_repository import UserRepository
from app.core.settings import settings


class AuthService:
    """Service xử lý authentication"""

    def __init__(self, repositories: Annotated[UserRepository, Depends()]):
        self.repositories = repositories

    def register(self, data: UserIn, session: Session) -> Dict[str, Any]:
        exist_user = self.repositories.get_by_email(data.email, session)
        if exist_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email đã được sử dụng"
            )
        # hashed password
        hashed = hash_password(data.password)
        user = User(
            email=data.email,
            username=data.username,
            password_hashed=hashed,
        )

        saved_user = self.repositories.create(data=user, session=session)

        if saved_user:
            return {"message": "Đăng ký thành công", "status": 200}

    def login(
        self, response: Response, data: OAuth2PasswordRequestForm, session: Session
    ) -> Dict[str, Any]:
        print("data: ", data)

        user = self.repositories.get_by_email(email=data.username, session=session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email không chính xác vui lòng thử lại",
            )

        password_hashed = user.get("password_hashed")
        if not verify_password(data.password, password_hashed):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Mật khẩu không chính xác vui lòng thử lại",
            )

        if user.get("status") == 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản đã bị vô hiệu hóa",
            )

        payload = {
            "user_id": str(user.get("id")),
            "email": user.get("email"),
            "role": user.get("role"),
        }

        access_token, exp_ts = create_access_token(payload)
        refresh_token, expire = create_refresh_token(payload)

        if isinstance(expire, datetime) and expire.tzinfo is None:
            expire = expire.replace(tzinfo=timezone.utc)

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            expires=expire,
            samesite="lax",
            secure=False,
        )
        return {
            "message": "Đăng nhập thành công",
            "access_token": access_token,
            "token_type": "bearer",
            "expiresIn": exp_ts,
        }
    
    def change_password(
        self,
        current_user: UserOut,
        old_password: str,
        new_password: str,
        session: Session,
    ) -> Dict[str, str]:
        # Lấy user raw từ DB để có password_hashed
        user = session.get(User, current_user.id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy tài khoản"
            )
        if not verify_password(old_password, user.password_hashed):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Mật khẩu cũ không đúng"
            )

        user.password_hashed = hash_password(new_password)
        session.add(user)
        session.commit()
        
        return {"message": "Đổi mật khẩu thành công"}

    def _generate_tokens_for_user(
        self, user: dict, response: Response
    ) -> Dict[str, Any]:
        """Helper: tạo access_token + refresh_token cho user dict (đã join role)"""
        payload = {
            "user_id": str(user.get("id")),
            "email": user.get("email"),
            "role": user.get("role"),
        }

        access_token, exp_ts = create_access_token(payload)
        refresh_token, expire = create_refresh_token(payload)

        if isinstance(expire, datetime) and expire.tzinfo is None:
            expire = expire.replace(tzinfo=timezone.utc)

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            expires=expire,
            samesite="lax",
            secure=False,
        )
        return {
            "message": "Đăng nhập thành công",
            "access_token": access_token,
            "token_type": "bearer",
            "expiresIn": exp_ts,
        }

    def _get_or_create_oauth_user(
        self, email: str, username: str, session: Session
    ) -> dict:
        """Tìm user theo email, nếu chưa có thì tạo mới (OAuth user)"""
        user = self.repositories.get_by_email(email, session)
        if user:
            return user

        # Tạo user mới với random password (OAuth user không cần password)
        random_password = hash_password(str(uuid4()))
        new_user = User(
            email=email,
            username=username,
            password_hashed=random_password,
        )
        self.repositories.create(data=new_user, session=session)
        # Lấy lại user với role join
        user = self.repositories.get_by_email(email, session)
        return user

    def google_login(
        self, data: GoogleLoginSchema, response: Response, session: Session
    ) -> Dict[str, Any]:
        """Đăng nhập bằng Google OAuth - nhận ID token từ frontend"""
        try:
            # Verify Google ID token
            # Google recommends verifying with their tokeninfo endpoint
            with httpx.Client() as client:
                google_response = client.get(
                    f"https://oauth2.googleapis.com/tokeninfo?id_token={data.credential}"
                )

            if google_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Google token không hợp lệ",
                )

            google_data = google_response.json()

            # Kiểm tra audience (client_id) để đảm bảo token thuộc app của mình
            if google_data.get("aud") != settings.GOOGLE_CLIENT_ID:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Google token không hợp lệ cho ứng dụng này",
                )

            email = google_data.get("email")
            name = google_data.get("name", email.split("@")[0])

            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Không lấy được email từ Google",
                )

            user = self._get_or_create_oauth_user(
                email=email, username=name, session=session
            )

            if user.get("status") == 0:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Tài khoản đã bị vô hiệu hóa",
                )

            return self._generate_tokens_for_user(user, response)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi xác thực Google: {str(e)}",
            )

    def facebook_login(
        self, data: FacebookLoginSchema, response: Response, session: Session
    ) -> Dict[str, Any]:
        """Đăng nhập bằng Facebook OAuth - nhận access token từ frontend"""
        try:
            # Verify Facebook access token bằng Graph API
            with httpx.Client() as client:
                fb_response = client.get(
                    "https://graph.facebook.com/me",
                    params={
                        "fields": "id,name,email",
                        "access_token": data.access_token,
                    },
                )

            if fb_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Facebook token không hợp lệ",
                )

            fb_data = fb_response.json()
            email = fb_data.get("email")
            name = fb_data.get("name", "Facebook User")

            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Không lấy được email từ Facebook. Vui lòng cấp quyền truy cập email.",
                )

            user = self._get_or_create_oauth_user(
                email=email, username=name, session=session
            )

            if user.get("status") == 0:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Tài khoản đã bị vô hiệu hóa",
                )

            return self._generate_tokens_for_user(user, response)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi xác thực Facebook: {str(e)}",
            )