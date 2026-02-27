import cloudinary
from cloudinary import Config

from .settings import settings


def cloud_config() -> Config: 
    return cloudinary.config( 
        cloud_name=settings.CLOUDINARY_CLOUD_NAME, 
        api_key = settings.CLOUDINARY_API_KEY, 
        api_secret=settings.CLOUDINARY_API_SECRET
    )