from sqlmodel import Session

from iccore.database import get_db_engine


def get_session():
    with Session(get_db_engine()) as session:
        yield session
