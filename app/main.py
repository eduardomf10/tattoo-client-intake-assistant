"""Tattoo Client Intake Assistant - FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.routers import intake, leads

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    init_db()
    yield


app = FastAPI(
    title="Tattoo Client Intake Assistant",
    description="API to analyze and structure tattoo client messages for studios",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(intake.router)
app.include_router(leads.router)


@app.get("/")
def root():
    """Root endpoint - health check and API info."""
    return {
        "service": "Tattoo Client Intake Assistant",
        "status": "running",
        "docs": "/docs",
    }
