from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY : str
    REFRESH_TOKEN_KEY:str
    ALGORITHM : str
    ACCESS_TOKEN_EXPIRE_MINUTES : int
    REFRESH_TOKEN_EXPIRE_DAYS:int
    DATABASE_URL : str
    CLOUDINARY_CLOUD_NAME:str
    CLOUDINARY_API_KEY:int
    CLOUDINARY_API_SECRET:str
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    
    # Facebook OAuth
    FACEBOOK_APP_ID: str = ""
    FACEBOOK_APP_SECRET: str = ""
    
    # VNPay Configuration
    VNPAY_TMN_CODE: str = "VNPAY_SANDBOX"
    VNPAY_HASH_SECRET: str = "SANDBOX_SECRET"
    VNPAY_PAYMENT_URL: str = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
    VNPAY_RETURN_URL: str = "http://localhost:3000/checkout/result"
    
    # GoShip Configuration
    GOSHIP_API_URL: str = "https://sandbox.goship.io/api/v2"
    GOSHIP_CLIENT_ID: int = 0
    GOSHIP_CLIENT_SECRET: str = ""
    
    # GoShip Shop Address (địa chỉ kho gửi hàng)
    GOSHIP_FROM_NAME: str = "E-Commerce Shop"
    GOSHIP_FROM_PHONE: str = "0123456789"
    GOSHIP_FROM_STREET: str = "123 Nguyễn Huệ"
    GOSHIP_FROM_WARD: int = 0
    GOSHIP_FROM_DISTRICT: int = 0
    GOSHIP_FROM_CITY: int = 0
    
    class Config: 
        env_file = '.env'   

settings = Settings()