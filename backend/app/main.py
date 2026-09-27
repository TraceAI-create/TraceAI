from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.decisions import router as decisions_router
from app.api.evidence import router as evidence_router
from app.api.policies import router as policies_router

app = FastAPI(
    title="TraceAI",
    description="AI Decision Traceability and Audit System: Capture -> Store -> Replay -> Review -> Trust",
    version="0.2.0",
)

# Enable CORS for local frontend development (e.g. Vite on localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(decisions_router)
app.include_router(evidence_router)
app.include_router(policies_router)


@app.get("/")
def root():
    return {
        "message": "TraceAI backend is running",
        "docs_url": "/docs",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "traceai",
    }