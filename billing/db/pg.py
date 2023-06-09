import runpy

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from core.config import settings

DATA_BASE = f'postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}/{settings.postgres_db}'

engine = create_async_engine(DATA_BASE, echo=False)
Base = declarative_base()
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    # init миграции можно сделать руками, а не как ниже.
    # В папке billing:
    # alembic revision -m "init" --autogenerate
    # alembic upgrade head
    # Собственно доп. миграции по аналогии.
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_pg() -> AsyncSession:
    async with async_session() as session:
        yield session
