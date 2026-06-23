"""
CivicLens — FastAPI Backend Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/")
def root():
    return {"message": "CivicLens API is running", "version": "0.1.0"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


# TODO: Register routers
# from backend.api.routes import upload, query, report
# app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
# app.include_router(query.router, prefix="/api/query", tags=["query"])
# app.include_router(report.router, prefix="/api/report", tags=["report"])
