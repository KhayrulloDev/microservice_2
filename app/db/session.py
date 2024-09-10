import os
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

USERNAME = os.getenv("POSTGRES_USER")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB = os.getenv("POSTGRES_DB")
HOSTNAME = os.getenv("POSTGRES_HOSTNAME")

SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{USERNAME}:{PASSWORD}@{HOSTNAME}/{DB}"

Base = declarative_base()

__engine = None
__async_session = None

def get_or_create_engine() -> AsyncEngine:
    global __engine
    if not __engine:
        __engine = create_async_engine(
            SQLALCHEMY_DATABASE_URL,
            future=True,
            echo=True,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=1800,
        )
    return __engine

def get_or_create_session() -> AsyncSession:
    global __async_session, __engine
    if not __engine:
        get_or_create_engine()
    if not __async_session:
        __async_session = sessionmaker(__engine, expire_on_commit=False, class_=AsyncSession)
    return __async_session()

async def dispose_engine():
    global __engine
    if __engine:
        await __engine.dispose()
    __engine = None
