"""Custom Image Classification Service using YOLO model"""

import logging
from typing import Dict, Any, Optional
import time
from pathlib import Path
import io
from PIL import Image

logger = logging.getLogger(__name__)


class ImageClassifierService:
    """Custom YOLO model for human pose classification"""
    
    def __init__(self, model_path: str = "models/best.pt"):
        """Initialize YOLO model"""
        self.model = None
        self.model_path = Path(model_path)
        self.classes = ["lying", "standing", "sitting"]
        
        try:
            # Try to load YOLO model
            from ultralytics import YOLO
            
            if self.model_path.exists():
                self.model = YOLO(str(self.model_path))
                logger.info(f"YOLO model loaded from {model_path}")
            else:
                logger.warning(f"Model file not found: {model_path}")
                logger.info("Using mock predictions")
                
        except ImportError:
            logger.warning("ultralytics not installed. Install with: pip install ultralytics")
            logger.info("Using mock predictions")
        except Exception as e:
            logger.error(f"Model loading error: {str(e)}")
            logger.info("Using mock predictions")
    
    async def classify_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Classify human pose from image
        
        Args:
            image_bytes: Image file as bytes
            
        Returns:
            Dictionary with classification results
        """
        start_time = time.time()
        
        if not self.model:
            return self._mock_classification()
        
        try:
            # Load image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Run inference
            results = self.model(image, verbose=False)
            
            # Get predictions
            if len(results) > 0 and len(results[0].boxes) > 0:
                # Get the best detection
                boxes = results[0].boxes
                confidences = boxes.conf.cpu().numpy()
                classes = boxes.cls.cpu().numpy()
                
                # Find highest confidence detection
                best_idx = confidences.argmax()
                best_class_idx = int(classes[best_idx])
                best_confidence = float(confidences[best_idx])
                
                # Get class name
                class_names = results[0].names
                predicted_class = class_names[best_class_idx]
                
                # Calculate scores for all classes
                all_scores = {class_names[i]: 0.0 for i in range(len(class_names))}
                for cls_idx, conf in zip(classes, confidences):
                    cls_name = class_names[int(cls_idx)]
                    all_scores[cls_name] = max(all_scores[cls_name], float(conf))
                
                result = {
                    "pose": predicted_class,
                    "confidence": best_confidence,
                    "all_scores": all_scores,
                    "detections_count": len(boxes),
                    "processing_time": time.time() - start_time
                }
                
                logger.info(f"Classification result: {predicted_class} ({best_confidence:.2f})")
                return result
            else:
                # No detections
                return {
                    "pose": "unknown",
                    "confidence": 0.0,
                    "all_scores": {cls: 0.0 for cls in self.classes},
                    "detections_count": 0,
                    "processing_time": time.time() - start_time,
                    "message": "No human detected in image"
                }
                
        except Exception as e:
            logger.error(f"Image classification error: {str(e)}")
            return self._mock_classification()
    
    def _mock_classification(self) -> Dict[str, Any]:
        """Mock classification for demo purposes"""
        import random
        
        pose = random.choice(self.classes)
        confidence = random.uniform(0.7, 0.95)
        
        all_scores = {}
        for cls in self.classes:
            if cls == pose:
                all_scores[cls] = confidence
            else:
                all_scores[cls] = random.uniform(0.05, 0.3)
        
        return {
            "pose": pose,
            "confidence": confidence,
            "all_scores": all_scores,
            "detections_count": 1,
            "processing_time": 0.15,
            "message": "Using mock classification (model not loaded)"
        }


# Singleton instance
image_classifier = ImageClassifierService()
