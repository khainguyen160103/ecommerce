from sqlalchemy.orm import Session
from app.models.user_model import User
from app.models.role_model import Role
from app.utils.auth_helper import hash_password
from app.core.settings import settings



def seed_roles(db: Session):
    """Tạo các role mặc định nếu chưa có."""
    roles = [
        {"id": 0, "name": "ADMIN"},
        {"id": 1, "name": "USER"},
        # Thêm các role khác nếu cần
    ]
    for role in roles:
        if not db.query(Role).filter_by(id=role["id"]).first():
            db.add(Role(id=role["id"], name=role["name"]))
    db.commit()

def seed_admin(db: Session):
    """Tạo admin nếu chưa có."""
    admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
    if not admin:
        db.add(User(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            password=hash_password(settings.ADMIN_PASSWORD),
            role_id=0,
            is_active=True,
        ))
        db.commit()