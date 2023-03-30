from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from core.config import settings as SETT

DATA_BASE = f'postgresql://{SETT.POSTGRES_USER}:{SETT.POSTGRES_PASSWORD}@{SETT.DB_DOCKER_HOST}/{SETT.POSTGRES_DB}'

engine = create_engine(DATA_BASE, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import models.db_models
    Base.metadata.create_all(bind=engine)
