"""Image Classification Endpoints"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import uuid
import logging
from datetime import datetime

from app.services.image_classifier import image_classifier
from app.services.blob_storage import blob_service
from app.services.monitoring import log_event_to_insights

router = APIRouter()
logger = logging.getLogger(__name__)


async def save_image_to_blob(request_id: str, image_bytes: bytes, filename: str, result: dict):
    """Background task to save image and results to Blob Storage"""
    # Save image
    image_url = await blob_service.save_input_file(
        f"{request_id}_{filename}",
        image_bytes,
        "image/jpeg"
    )
    
    # Save results
    log_data = {
        "request_id": request_id,
        "endpoint": "image_classification",
        "filename": filename,
        "image_url": image_url,
        "result": result,
        "timestamp": datetime.utcnow().isoformat()
    }
    await blob_service.save_request_log(request_id, log_data)


@router.post("/classify-pose")
async def classify_human_pose(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...)
):
    """
    Classify human pose from image
    
    - **image**: Upload an image file (JPG, PNG)
    
    Returns pose classification: lying, standing, or sitting
    """
    request_id = str(uuid.uuid4())
    
    # Validate file type
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Track event
        log_event_to_insights("image_classification_request", {
            "request_id": request_id,
            "filename": image.filename,
            "content_type": image.content_type
        })
        
        # Read image bytes
        image_bytes = await image.read()
        
        # Classify image
        result = await image_classifier.classify_image(image_bytes)
        
        # Prepare response
        response = {
            "filename": image.filename,
            "pose": result["pose"],
            "confidence": result["confidence"],
            "all_scores": result["all_scores"],
            "detections_count": result.get("detections_count", 0),
            "processing_time": result["processing_time"],
            "request_id": request_id
        }
        
        if "message" in result:
            response["message"] = result["message"]
        
        # Save to Blob Storage in background
        background_tasks.add_task(
            save_image_to_blob,
            request_id,
            image_bytes,
            image.filename,
            result
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Image classification error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model-info")
async def get_model_info():
    """
    Get information about the loaded model
    """
    return {
        "model": "YOLOv8 Custom",
        "model_path": str(image_classifier.model_path),
        "model_loaded": image_classifier.model is not None,
        "classes": image_classifier.classes,
        "description": "Human pose classification: lying, standing, sitting"
    }
