from typing import  TypedDict
from fastapi import  Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class FastAPIAppContext(BaseModel):
    """
    Context for the FastAPI app
    """

    # embedding_column: str
    # cfg: Optional[Settings] = None


class State(TypedDict):
    sessionmaker: async_sessionmaker[AsyncSession]
    context: FastAPIAppContext


async def get_context(
    request: Request,
) -> FastAPIAppContext:
    return request.state.context
