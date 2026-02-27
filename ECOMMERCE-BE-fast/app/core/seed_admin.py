from sqlalchemy.orm import Session
from app.models.user_model import User
from app.models.role_model import Role
from app.utils.auth_helper import hash_password
from app.core.settings import settings
from app.core.database import get_session


def seed_roles(db: Session):
    """Tạo các role mặc định nếu chưa có."""
    roles = [
        {"id": 1, "description": "ADMIN"},
        {"id": 2, "description": "USER"},
        # Thêm các role khác nếu cần
    ]
    for role in roles:
        if not db.query(Role).filter_by(id=role["id"]).first():
            db.add(Role(id=role["id"], description=role["description"]))
    db.commit()

def seed_admin(db: Session):
    """Tạo admin nếu chưa có."""
    admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
    if not admin:
        db.add(User(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            password_hashed=hash_password(settings.ADMIN_PASSWORD),
            role_id=1,
            is_active=True,
        ))
        db.commit()
def run_seeders():
    with next(get_session()) as db:
        seed_roles(db)
        seed_admin(db)


if __name__ == "__main__":
    run_seeders()