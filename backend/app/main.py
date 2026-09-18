from fastapi import FastAPI

app = FastAPI(
    title="TRACEAI",
    description="AI Decision Traceability and Audit System",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "message": "TRACEAI backend is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }