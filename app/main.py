import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routers import auth
from app.utils.seed_admin import create_default_admin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting Quiz Platform API")
    create_default_admin()
    yield
    # Shutdown
    logger.info("Shutting down Quiz Platform API")

app = FastAPI(
    title="Online Quiz Platform API",
    description="A RESTful API backend using FastAPI for an online quiz platform",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(auth.router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    messages = [f"{'.'.join(map(str, err['loc'][1:]))}: {err['msg']}" for err in errors]

    return JSONResponse(
        status_code=400,
        content={"detail": messages if len(messages) > 1 else messages[0]}
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Online Quiz Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}