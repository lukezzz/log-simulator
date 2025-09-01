from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.db.session import get_db, create_tables
from core.db.init_data import create_default_log_templates
from api import jobs, log_templates, tools

db = get_db().__next__()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables on startup."""
    create_tables()
    create_default_log_templates(db)

    yield
    db.close()


app = FastAPI(
        title="Log Simulator API",
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

# Include routers
app.include_router(jobs.router)
app.include_router(log_templates.router)
app.include_router(tools.router)
