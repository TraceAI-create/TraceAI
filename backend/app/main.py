from fastapi import FastAPI

from app.api.decisions import router as decisions_router


app = FastAPI(
    title="TRACEAI",
    description="AI Decision Traceability and Audit System",
    version="0.1.0",
)


app.include_router(decisions_router)


@app.get("/")
def root():
    return {
        "message": "TRACEAI backend is running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "traceai",
    }