from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import settings
from model.orm import Base


engine = create_async_engine(settings.db_url, echo=True)
async_session_maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def make_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def clean_db():
    await engine.dispose()
