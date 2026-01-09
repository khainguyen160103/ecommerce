from sqlmodel import SQLModel , create_engine , Session
from typing import Generator
from app.models.user_model import User
from app.models.role_model import Role

DATABASE_URL = "mysql+pymysql://root:162003@localhost:3306/ecommerce"

engine = create_engine(DATABASE_URL ,echo=True)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
