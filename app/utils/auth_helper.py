
from pwdlib import PasswordHash


def hash_password(password:str) -> str: 
    password_hash = PasswordHash.recommended()
    return  password_hash.hash(password=password)

 

def verify_password(user_password: str, password_hashed : str) -> bool:
    password_hash = PasswordHash.recommended()
    return password_hash.verify(user_password,password_hashed)
