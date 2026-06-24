"""
CivicLens — FastAPI Backend Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.utils.database import Base, engine
from backend.api.models import dataset as dataset_models  # registers models with Base
from backend.api.routes import upload

app = FastAPI(
    title="CivicLens API",
    description="Nonprofit Data Analytics Assistant powered by Claude",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create all tables automatically on startup (safe — won't drop existing tables)
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "CivicLens API is running", "version": "0.1.0"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


# Registered routers
app.include_router(upload.router, prefix="/api", tags=["upload"])
