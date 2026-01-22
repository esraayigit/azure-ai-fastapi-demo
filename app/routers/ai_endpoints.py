"""AI Service endpoints"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
import uuid
import logging
from datetime import datetime

from app.models.schemas import (
    SentimentAnalysisRequest,
    SentimentAnalysisResponse,
    TextClassificationRequest,
    TextClassificationResponse,
    OpenAIRequest,
    OpenAIResponse,
    ErrorResponse
)
from app.services.ai_service import ai_service
from app.services.blob_storage import blob_service
from app.services.monitoring import log_event_to_insights

router = APIRouter()
logger = logging.getLogger(__name__)


async def save_request_to_blob(request_id: str, endpoint: str, request_data: dict, response_data: dict):
    """Background task to save request/response to Blob Storage"""
    log_data = {
        "request_id": request_id,
        "endpoint": endpoint,
        "request": request_data,
        "response": response_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    await blob_service.save_request_log(request_id, log_data)


@router.post("/sentiment", response_model=SentimentAnalysisResponse)
async def analyze_sentiment(
    request: SentimentAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Analyze sentiment of text
    
    - **text**: Text to analyze (max 5000 characters)
    - **language**: Language code (default: en)
    
    Returns sentiment (positive/negative/neutral) with confidence scores
    """
    request_id = str(uuid.uuid4())
    
    try:
        # Track event
        log_event_to_insights("sentiment_analysis_request", {
            "request_id": request_id,
            "text_length": len(request.text),
            "language": request.language
        })
        
        # Call AI service
        result = await ai_service.analyze_sentiment(request.text, request.language)
        
        response = SentimentAnalysisResponse(
            text=request.text,
            sentiment=result["sentiment"],
            confidence=result["confidence"],
            scores=result["scores"],
            processing_time=result["processing_time"],
            request_id=request_id
        )
        
        # Save to Blob Storage in background
        background_tasks.add_task(
            save_request_to_blob,
            request_id,
            "sentiment_analysis",
            request.dict(),
            response.dict()
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Sentiment analysis error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify", response_model=TextClassificationResponse)
async def classify_text(
    request: TextClassificationRequest,
    background_tasks: BackgroundTasks
):
    """
    Classify text into categories
    
    - **text**: Text to classify (max 5000 characters)
    - **categories**: Optional custom categories
    
    Returns the best matching category with confidence scores
    """
    request_id = str(uuid.uuid4())
    
    try:
        # Track event
        log_event_to_insights("text_classification_request", {
            "request_id": request_id,
            "text_length": len(request.text),
            "has_custom_categories": bool(request.categories)
        })
        
        # Call AI service
        result = await ai_service.classify_text(request.text, request.categories)
        
        response = TextClassificationResponse(
            text=request.text,
            category=result["category"],
            confidence=result["confidence"],
            all_scores=result["all_scores"],
            processing_time=result["processing_time"],
            request_id=request_id
        )
        
        # Save to Blob Storage in background
        background_tasks.add_task(
            save_request_to_blob,
            request_id,
            "text_classification",
            request.dict(),
            response.dict()
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Text classification error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=OpenAIResponse)
async def chat_completion(
    request: OpenAIRequest,
    background_tasks: BackgroundTasks
):
    """
    Get AI chat completion
    
    - **prompt**: User prompt (max 5000 characters)
    - **max_tokens**: Maximum tokens to generate (1-4000, default: 150)
    - **temperature**: Sampling temperature (0-2, default: 0.7)
    
    Returns AI-generated response
    """
    request_id = str(uuid.uuid4())
    
    try:
        # Track event
        log_event_to_insights("chat_completion_request", {
            "request_id": request_id,
            "prompt_length": len(request.prompt),
            "max_tokens": request.max_tokens,
            "temperature": request.temperature
        })
        
        # Call AI service
        result = await ai_service.chat_completion(
            request.prompt,
            request.max_tokens,
            request.temperature
        )
        
        response = OpenAIResponse(
            prompt=request.prompt,
            response=result["response"],
            model=result["model"],
            tokens_used=result["tokens_used"],
            processing_time=result["processing_time"],
            request_id=request_id
        )
        
        # Save to Blob Storage in background
        background_tasks.add_task(
            save_request_to_blob,
            request_id,
            "chat_completion",
            request.dict(),
            response.dict()
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Chat completion error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_api_stats():
    """
    Get API usage statistics
    
    Returns basic statistics about API usage
    """
    return {
        "message": "API statistics endpoint",
        "note": "In production, this would query Application Insights for real metrics"
    }
