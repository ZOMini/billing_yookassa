from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

from config import settings as SETT

DATA_BASE = f'postgresql://{SETT.POSTGRES_USER}:{SETT.POSTGRES_PASSWORD}@{SETT.POSTGRES_HOST}/{SETT.POSTGRES_DB}'

engine = create_engine(DATA_BASE)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    Base.metadata.create_all(bind=engine)
