import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from models.base import Base


db_cfg = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', 5432),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', ''),
    'database': os.getenv('POSTGRES_DB', 'courts'),
}


def get_url(host='localhost', port=5432, user='postgres', password='', database='courts'):
    return URL(
        'postgresql', username=user, password=password, port=port, host=host, database=database)


default_url = get_url(**db_cfg)
engine = create_engine(default_url)
Session = sessionmaker(bind=engine)
@contextmanager
def get_session():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def _create_db(host='localhost', port=5432, user='postgres', password='', database='courts'):
    db_url = get_url(host, port, user, password, database)
    if database_exists(db_url):
        drop_database(db_url)
    create_database(db_url)


def recreate_db():
    _create_db(**db_cfg)
    Base.metadata.create_all(bind=engine)
