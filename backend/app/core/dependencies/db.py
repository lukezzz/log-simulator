from typing import Annotated
from fastapi import Depends, Request
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker


async def create_async_sessionmaker(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Get the agent database"""
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_async_sessionmaker(
    request: Request,
) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    yield request.state.sessionmaker


async def get_async_db_session(
    sessionmaker: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_sessionmaker)
    ],
) -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        yield session


DBSession = Annotated[AsyncSession, Depends(get_async_db_session)]


# async def get_async_replica_sessionmaker(
#     request: Request,
# ) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
#     yield request.state.replica_sessionmaker

# async def get_async_db_replica_session(
#     sessionmaker: Annotated[
#         async_sessionmaker[AsyncSession], Depends(get_async_replica_sessionmaker)
#     ],
# ) -> AsyncGenerator[AsyncSession, None]:
#     async with sessionmaker() as session:
#         yield session

