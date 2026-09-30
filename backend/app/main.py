"""Main FastAPI application entry point for TraceAI.

This module initializes the FastAPI app, sets up CORS settings,
and registers all API routers for decisions, evidence, policies, and replays.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.decisions import router as decisions_router
from app.api.evidence import router as evidence_router
from app.api.policies import router as policies_router
from app.api.replay import router as replay_router

# Initialize the main FastAPI application
app = FastAPI(
    title="TraceAI",
    description="AI Decision Traceability and Audit System: Capture -> Store -> Replay -> Review -> Trust",
    version="0.3.0",
)

# Enable CORS for local frontend development (for example, Vite on localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route handlers
app.include_router(decisions_router)
app.include_router(evidence_router)
app.include_router(policies_router)
app.include_router(replay_router)


@app.get("/")
def root():
    """Return a welcome message and a link to the API documentation."""
    return {
        "message": "TraceAI backend is running",
        "docs_url": "/docs",
    }


@app.get("/health")
def health():
    """Return the health status of the service."""
    return {
        "status": "healthy",
        "service": "traceai",
    }
