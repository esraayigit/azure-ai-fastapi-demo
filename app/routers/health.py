"""Health check endpoints"""

from fastapi import APIRouter
from datetime import datetime

from app.models.schemas import HealthResponse
from app.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns the health status of the application and Azure services
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        azure_services={
            "azure_ai": bool(settings.AZURE_AI_ENDPOINT and settings.AZURE_AI_KEY),
            "blob_storage": bool(settings.AZURE_STORAGE_CONNECTION_STRING),
            "app_insights": bool(settings.APPINSIGHTS_INSTRUMENTATIONKEY)
        }
    )


@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Azure AI FastAPI Demo",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
