from app.core.settings import settings
from datetime import datetime, timedelta, timezone
import jwt
from typing import Dict ,Any, Tuple
from jwt.exceptions import ExpiredSignatureError, DecodeError, InvalidTokenError
from .response_helper import ResponseHandler
def create_access_token(data: dict) -> Tuple[str, str]:
    to_encode = data.copy()
    print("time---------------" , settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    exp_ts = expire.timestamp()
    to_encode.update({"exp": exp_ts})
    access_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return access_token , exp_ts

def create_refresh_token(data:dict) -> str:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS) 
    to_encode.update({"exp": expire})
    refresh_token = jwt.encode(to_encode, settings.REFRESH_TOKEN_KEY, algorithm=settings.ALGORITHM)
    return refresh_token, expire

def verify_token(token:str): 
   try: 
     return jwt.decode(token,settings.SECRET_KEY,settings.ALGORITHM)
   except ExpiredSignatureError: 
      return ResponseHandler.error(
         "Token Has Experied",
         401
      )
   except DecodeError: 
      return ResponseHandler.error( 
         "Token Was Error", 
         500
      )
   except InvalidTokenError: 
      return ResponseHandler.error( 
         "Token Error",
         401
      )