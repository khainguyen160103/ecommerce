from pydantic import BaseModel
from typing import Any

class LoginSchema(BaseModel):
    email: str
    password: str

class ResponseLogin(BaseModel): 
    message: str
    access_token:str
    token_type:str

class GoogleLoginSchema(BaseModel):
    credential: str  # Google ID token from frontend

class FacebookLoginSchema(BaseModel):
    access_token: str  # Facebook access token from frontend

class ChangePasswordSchema(BaseModel):
    old_password: str
    new_password: str