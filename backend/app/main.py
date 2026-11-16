"""
app/main.py
FastAPI application entry point for SamaadSetu Voice Grievance Portal.
"""
from __future__ import annotations

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api.tickets import router as legacy_tickets_router
from app.api.routes import router as pipeline_routes_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Voice-First Pictorial Citizen Grievance Portal & Officer Triage Desk",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(legacy_tickets_router, prefix=settings.API_V1_PREFIX)
app.include_router(pipeline_routes_router)

BASE_DIR = Path(__file__).resolve().parent.parent.parent


@app.get("/health", tags=["system"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
        "dialects_supported": ["hi-IN", "awa-IN", "bho-IN", "en-IN"]
    }


@app.get("/", response_class=HTMLResponse, tags=["citizen"])
async def serve_citizen_portal():
    citizen_file = BASE_DIR / "index.html"
    if citizen_file.exists():
        return FileResponse(citizen_file)
    return HTMLResponse("<h1>SamaadSetu Citizen Portal: index.html not found</h1>", status_code=404)


@app.get("/officer", response_class=HTMLResponse, tags=["officer"])
async def serve_officer_workbench():
    officer_file = BASE_DIR / "officer.html"
    if officer_file.exists():
        return FileResponse(officer_file)
    return HTMLResponse("<h1>Officer Triage Workbench: officer.html not found</h1>", status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
