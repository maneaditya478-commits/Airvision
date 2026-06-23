from collections.abc import AsyncGenerator
import ssl
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine

from app.config import get_settings

settings = get_settings()

# Configure ssl for asyncpg dynamically if sslmode is present
db_url = settings.database_url
connect_args = {}

parsed = urlparse(db_url)
query_params = parse_qs(parsed.query)
sslmode = query_params.pop("sslmode", [None])[0]

if sslmode in ["require", "prefer", "allow", "verify-ca", "verify-full"]:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ctx

new_query = urlencode(query_params, doseq=True)
clean_db_url = urlunparse((
    parsed.scheme,
    parsed.netloc,
    parsed.path,
    parsed.params,
    new_query,
    parsed.fragment
))

engine = create_async_engine(
    clean_db_url,
    echo=settings.debug,
    pool_pre_ping=True,
    connect_args=connect_args
)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

sync_engine = create_engine(settings.database_url_sync, pool_pre_ping=True)
SyncSessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()
