from fastapi import HTTPException, status
from sqlalchemy.engine import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from src.conf.config import settings


engine = create_engine(settings.sqlalchemy_database_url)
DBSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():

    """
    The get_db function is a context manager that will automatically close the database connection
    when it goes out of scope.
    It also handles any exceptions that occur within the with block, rolling back any changes to the database
    and closing the session before re-raising them.

    :return: A database connection
    :doc-author: Trelent
    """
    db = DBSession()
    try:
        yield db
    except SQLAlchemyError as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    finally:
        db.close()
