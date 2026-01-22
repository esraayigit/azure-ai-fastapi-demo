"""Azure AI Services Integration"""

import logging
from typing import Dict, Any, Optional
import time
from openai import AzureOpenAI

from app.config import settings

logger = logging.getLogger(__name__)


class AzureAIService:
    """Azure AI Services wrapper"""
    
    def __init__(self):
        """Initialize Azure AI client"""
        self.client = None
        
        if settings.AZURE_AI_ENDPOINT and settings.AZURE_AI_KEY:
            try:
                self.client = AzureOpenAI(
                    api_key=settings.AZURE_AI_KEY,
                    api_version=settings.AZURE_OPENAI_API_VERSION,
                    azure_endpoint=settings.AZURE_AI_ENDPOINT
                )
                logger.info("Azure OpenAI client initialized")
            except Exception as e:
                logger.warning(f"Azure OpenAI client initialization failed: {str(e)}")
                self.client = None
        else:
            logger.warning("Azure AI credentials not configured, using mock responses")
    
    async def analyze_sentiment(self, text: str, language: str = "en") -> Dict[str, Any]:
        """
        Analyze sentiment using Azure OpenAI
        
        Args:
            text: Text to analyze
            language: Language code
            
        Returns:
            Dictionary with sentiment analysis results
        """
        start_time = time.time()
        
        if not self.client:
            # Mock response for demo purposes
            return self._mock_sentiment_analysis(text)
        
        try:
            prompt = f"""Analyze the sentiment of the following text and respond with a JSON object containing:
- sentiment: one of "positive", "negative", or "neutral"
- confidence: a float between 0 and 1
- scores: an object with scores for positive, negative, and neutral

Text: {text}

Respond only with the JSON object, no additional text."""

            response = self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a sentiment analysis AI. Respond only with JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            import json
            result = json.loads(result_text)
            result['processing_time'] = time.time() - start_time
            
            return result
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return self._mock_sentiment_analysis(text)
    
    async def classify_text(self, text: str, categories: Optional[list] = None) -> Dict[str, Any]:
        """
        Classify text using Azure OpenAI
        
        Args:
            text: Text to classify
            categories: Optional custom categories
            
        Returns:
            Dictionary with classification results
        """
        start_time = time.time()
        
        if not self.client:
            return self._mock_text_classification(text)
        
        try:
            default_categories = ["Technology", "Business", "Sports", "Entertainment", "Politics", "Health"]
            cats = categories if categories else default_categories
            
            prompt = f"""Classify the following text into one of these categories: {', '.join(cats)}

Text: {text}

Respond with a JSON object containing:
- category: the best matching category
- confidence: a float between 0 and 1
- all_scores: an object with confidence scores for each category

Respond only with the JSON object."""

            response = self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a text classification AI. Respond only with JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            result_text = response.choices[0].message.content.strip()
            
            import json
            result = json.loads(result_text)
            result['processing_time'] = time.time() - start_time
            
            return result
            
        except Exception as e:
            logger.error(f"Text classification error: {str(e)}")
            return self._mock_text_classification(text)
    
    async def chat_completion(self, prompt: str, max_tokens: int = 150, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Get chat completion from Azure OpenAI
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Dictionary with completion results
        """
        start_time = time.time()
        
        if not self.client:
            return {
                "response": "Azure OpenAI is not configured. This is a mock response.",
                "model": "mock",
                "tokens_used": 0,
                "processing_time": time.time() - start_time
            }
        
        try:
            response = self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return {
                "response": response.choices[0].message.content,
                "model": settings.AZURE_OPENAI_DEPLOYMENT,
                "tokens_used": response.usage.total_tokens,
                "processing_time": time.time() - start_time
            }
            
        except Exception as e:
            logger.error(f"Chat completion error: {str(e)}")
            raise
    
    def _mock_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Mock sentiment analysis for demo"""
        text_lower = text.lower()
        
        # Simple keyword-based mock analysis
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "love", "happy"]
        negative_words = ["bad", "terrible", "awful", "horrible", "hate", "sad", "angry", "poor"]
        
        positive_score = sum(1 for word in positive_words if word in text_lower) / 10
        negative_score = sum(1 for word in negative_words if word in text_lower) / 10
        neutral_score = 1.0 - positive_score - negative_score
        
        if positive_score > negative_score:
            sentiment = "positive"
            confidence = min(0.5 + positive_score, 0.95)
        elif negative_score > positive_score:
            sentiment = "negative"
            confidence = min(0.5 + negative_score, 0.95)
        else:
            sentiment = "neutral"
            confidence = 0.6
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "scores": {
                "positive": min(positive_score + 0.3, 1.0) if sentiment == "positive" else positive_score,
                "negative": min(negative_score + 0.3, 1.0) if sentiment == "negative" else negative_score,
                "neutral": neutral_score
            },
            "processing_time": 0.1
        }
    
    def _mock_text_classification(self, text: str) -> Dict[str, Any]:
        """Mock text classification for demo"""
        categories = ["Technology", "Business", "Sports", "Entertainment", "Politics", "Health"]
        
        # Simple keyword matching
        keywords = {
            "Technology": ["tech", "software", "computer", "ai", "data", "cloud", "app"],
            "Business": ["business", "company", "market", "revenue", "profit", "investment"],
            "Sports": ["sports", "game", "team", "player", "match", "championship"],
            "Entertainment": ["movie", "music", "film", "show", "celebrity", "entertainment"],
            "Politics": ["politics", "government", "election", "president", "policy"],
            "Health": ["health", "medical", "doctor", "hospital", "disease", "treatment"]
        }
        
        text_lower = text.lower()
        scores = {}
        
        for category, words in keywords.items():
            score = sum(1 for word in words if word in text_lower) / len(words)
            scores[category] = min(score + 0.1, 0.9)
        
        # Find best category
        best_category = max(scores.items(), key=lambda x: x[1])
        
        return {
            "category": best_category[0],
            "confidence": best_category[1],
            "all_scores": scores,
            "processing_time": 0.1
        }


# Singleton instance
ai_service = AzureAIService()
