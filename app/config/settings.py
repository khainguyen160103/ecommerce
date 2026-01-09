from pydantic_settings import BaseSettings

class settings(BaseSettings):
    SECRET_KEY : str
    ALGORITHM : str
    ACCESS_TOKEN_EXPIRE_MINUTES : int
    DATABASE_URL : str
    class Config: 
        env_file = '.env'   