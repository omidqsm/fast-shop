from db import async_session_maker


async def get_db_session():
    session = async_session_maker()
    try:
        yield session
    finally:
        await session.close()