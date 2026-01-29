"""FastAPI Main Application"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import time

from app.routers import health, ai_endpoints, image_endpoints, auth
from app.config import settings
from app.services.monitoring import log_request_to_insights

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# initialize FastAPI app
app = FastAPI(
    title="Azure AI FastAPI Demo",
    description="AI API with Azure AI Services, Blob Storage, and Application Insights",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# middleware for request logging and monitoring
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests to Application Insights"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    # log to Application Insights
    log_request_to_insights(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration=process_time
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response


# exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# include routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(ai_endpoints.router, prefix="/api/v1", tags=["AI Services"])
app.include_router(image_endpoints.router, prefix="/api/v1", tags=["Image Classification"])


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("🚀 Azure AI FastAPI Demo started")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Azure AI Services: {'Configured' if settings.AZURE_AI_ENDPOINT else 'Not configured'}")
    logger.info(f"Blob Storage: {'Configured' if settings.AZURE_STORAGE_CONNECTION_STRING else 'Not configured'}")
    logger.info(f"Application Insights: {'Configured' if settings.APPINSIGHTS_INSTRUMENTATIONKEY else 'Not configured'}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("👋 Azure AI FastAPI Demo shutting down")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
