"""Pydantic models for request/response validation"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str
    azure_services: Dict[str, bool]


class SentimentAnalysisRequest(BaseModel):
    """Sentiment analysis request"""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to analyze")
    language: Optional[str] = Field("en", description="Language code (e.g., 'en', 'tr')")


class SentimentAnalysisResponse(BaseModel):
    """Sentiment analysis response"""
    text: str
    sentiment: str
    confidence: float
    scores: Dict[str, float]
    processing_time: float
    request_id: str


class TextClassificationRequest(BaseModel):
    """Text classification request"""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to classify")
    categories: Optional[list[str]] = Field(None, description="Optional custom categories")


class TextClassificationResponse(BaseModel):
    """Text classification response"""
    text: str
    category: str
    confidence: float
    all_scores: Dict[str, float]
    processing_time: float
    request_id: str


class OpenAIRequest(BaseModel):
    """OpenAI chat completion request"""
    prompt: str = Field(..., min_length=1, max_length=5000, description="User prompt")
    max_tokens: Optional[int] = Field(150, ge=1, le=4000, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(0.7, ge=0, le=2, description="Sampling temperature")


class OpenAIResponse(BaseModel):
    """OpenAI chat completion response"""
    prompt: str
    response: str
    model: str
    tokens_used: int
    processing_time: float
    request_id: str


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    request_id: Optional[str] = None
    timestamp: datetime
