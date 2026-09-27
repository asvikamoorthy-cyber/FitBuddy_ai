from .database import init_db
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initializes our SQLite database layout automatically when the application starts
    init_db()
    yield

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="FitBuddy - AI-powered fitness plan generator.",
    lifespan=lifespan,
)

# Safely includes the router engine after initialization blocks to bypass loops
from .routes import router
app.include_router(router)
