from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager
import os
import uuid

from app.api.router import router as api_router
from app.core.middleware import RequestIDMiddleware, request_id_ctx_var

from app.core.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    
    # Initialize the global tracer's storage
    from app.core.tracer import tracer
    from app.services.sqlite_storage import SQLiteStorage
    tracer.storage = SQLiteStorage()
    
    # Models are no longer loaded here directly.
    # They are loaded lazily via API dependencies (lru_cache) on first request.
    yield
    # Cleanup resources

app = FastAPI(
    title="RAG Observability Lab",
    description="Production API for the RAG Observability Lab platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
# In production, set CORS_ORIGINS enviroment variable (e.g. "https://myapp.com,https://other.com")
# If not set, defaults to wildcard for development.
origins = os.environ.get("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestIDMiddleware)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    req_id = request_id_ctx_var.get()
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(exc),
                "request_id": req_id
            }
        }
    )

app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

