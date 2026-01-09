from jose import JWTError, jwt
from app.config.settings import settings
from datetime import datetime, timedelta 

def create_access_token(data: dict , expires_delta : timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_token(token:str): 
    try: 
        payload = jwt.decode(token=token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError: 
        return None