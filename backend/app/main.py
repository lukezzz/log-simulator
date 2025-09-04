from fastapi import FastAPI
from collections.abc import AsyncIterator
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.dependencies.db import create_async_sessionmaker
from core.postgres_engine import create_pg_engine
from core.dependencies.context import State

from core.auth_jwt.auth_config import AuthConfig
from core.dependencies.redis import get_auth_redis
from core.settings import cfg, get_settings

from fastapi_pagination import add_pagination
from core.fastapi_logger import fastapi_logger


# from app.scripts.init_data import init_db_data
from api import auth, jobs, log_templates, tools


settings = get_settings()

fastapi_logger.setLevel(settings.LOGGING_LEVEL)

# 初始化auth_jwt
@AuthConfig.load_config
def get_config():
    return cfg


@AuthConfig.token_in_denylist_loader
async def token_in_denylist(raw_jwt_token):
    jti = raw_jwt_token["jti"]
    if not jti:
        return True
    rds = await get_auth_redis().__anext__()
    res = await rds.get(jti)
    return bool(res)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[State]:
    engine = await create_pg_engine()
    sessionmaker = await create_async_sessionmaker(engine)
    yield {
            "engine": engine,
            "sessionmaker": sessionmaker,
        }
    await engine.dispose()


app = FastAPI(
        title="Log Simulator Backend",
        description="API for managing and running the Log Simulator.",
        version="0.1.0",
        lifespan=lifespan
    )
    
# Configure CORS middleware for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_pagination(app)


# Include routers
app.include_router(auth.router, prefix="/auth")
app.include_router(jobs.router, prefix="/jobs")
app.include_router(log_templates.router, prefix="/log_templates")
app.include_router(tools.router, prefix="/tools")
