from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from sqlalchemy.orm import (
    Session,
    declarative_base,
    scoped_session,
    sessionmaker
)

from core.config import settings

DATA_BASE = f'postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}/{settings.postgres_db}'

engine = create_engine(DATA_BASE)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import models.models_pg
    Base.metadata.create_all(bind=engine)


def get_pg() -> scoped_session[Session]:
    return db_session
