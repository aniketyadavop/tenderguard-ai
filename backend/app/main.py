from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.database import engine, SessionLocal
from backend.app.services.seed_data import seed_database_benchmarks
from backend.app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Verify database connection and seed initial benchmark data
    try:
        with engine.connect() as conn:
            pass
        db = SessionLocal()
        try:
            seed_database_benchmarks(db)
            print(f"[{settings.PROJECT_NAME}] Database connected & benchmark dossiers seeded successfully.")
        finally:
            db.close()
    except Exception as exc:
        print(f"[{settings.PROJECT_NAME}] Warning: Database connection or seeding failed: {exc}")
    yield
    print(f"[{settings.PROJECT_NAME}] Shutting down gracefully.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan
)

# CORS Middleware for Vite / React frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "zero_retention_mode": settings.ZERO_RETENTION_MODE,
        "docs_url": f"{settings.API_V1_PREFIX}/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
