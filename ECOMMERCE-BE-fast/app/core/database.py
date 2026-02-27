from sqlmodel import SQLModel , create_engine , Session
from typing import Generator

DATABASE_URL = "mysql+pymysql://root:162003@mysql:3306/ecommerce"

engine = create_engine(DATABASE_URL ,echo=True)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
