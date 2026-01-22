"""Azure Blob Storage Service"""

import logging
from typing import Optional
from datetime import datetime
import json

from azure.storage.blob import BlobServiceClient, ContentSettings
from app.config import settings

logger = logging.getLogger(__name__)


class BlobStorageService:
    """Azure Blob Storage wrapper for logging and data persistence"""
    
    def __init__(self):
        """Initialize Blob Storage client"""
        if settings.AZURE_STORAGE_CONNECTION_STRING:
            try:
                self.client = BlobServiceClient.from_connection_string(
                    settings.AZURE_STORAGE_CONNECTION_STRING
                )
                self.container_name = settings.AZURE_STORAGE_CONTAINER_NAME
                self._ensure_container_exists()
                logger.info(f"Blob Storage initialized: container={self.container_name}")
            except Exception as e:
                logger.error(f"Blob Storage initialization error: {str(e)}")
                self.client = None
        else:
            self.client = None
            logger.warning("Blob Storage connection string not configured")
    
    def _ensure_container_exists(self):
        """Ensure the container exists"""
        try:
            container_client = self.client.get_container_client(self.container_name)
            if not container_client.exists():
                container_client.create_container()
                logger.info(f"Created container: {self.container_name}")
        except Exception as e:
            logger.error(f"Container creation error: {str(e)}")
    
    async def save_request_log(self, request_id: str, data: dict) -> bool:
        """
        Save request/response log to Blob Storage
        
        Args:
            request_id: Unique request identifier
            data: Request/response data to save
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.warning("Blob Storage not configured, skipping log save")
            return False
        
        try:
            # Create blob name with timestamp
            timestamp = datetime.utcnow().strftime("%Y%m%d")
            blob_name = f"logs/{timestamp}/{request_id}.json"
            
            # Add metadata
            data['logged_at'] = datetime.utcnow().isoformat()
            
            # Upload to blob
            blob_client = self.client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            blob_client.upload_blob(
                json.dumps(data, indent=2),
                overwrite=True,
                content_settings=ContentSettings(content_type='application/json')
            )
            
            logger.info(f"Saved log to blob: {blob_name}")
            return True
            
        except Exception as e:
            logger.error(f"Blob upload error: {str(e)}")
            return False
    
    async def save_input_file(self, file_name: str, file_content: bytes, content_type: str = "application/octet-stream") -> Optional[str]:
        """
        Save input file to Blob Storage
        
        Args:
            file_name: Name of the file
            file_content: File content as bytes
            content_type: MIME type of the file
            
        Returns:
            Blob URL if successful, None otherwise
        """
        if not self.client:
            logger.warning("Blob Storage not configured, skipping file save")
            return None
        
        try:
            # Create blob name with timestamp
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            blob_name = f"inputs/{timestamp}_{file_name}"
            
            # Upload to blob
            blob_client = self.client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            blob_client.upload_blob(
                file_content,
                overwrite=True,
                content_settings=ContentSettings(content_type=content_type)
            )
            
            blob_url = blob_client.url
            logger.info(f"Saved file to blob: {blob_name}")
            return blob_url
            
        except Exception as e:
            logger.error(f"File upload error: {str(e)}")
            return None
    
    async def get_log(self, request_id: str, date: str) -> Optional[dict]:
        """
        Retrieve a log from Blob Storage
        
        Args:
            request_id: Unique request identifier
            date: Date in YYYYMMDD format
            
        Returns:
            Log data if found, None otherwise
        """
        if not self.client:
            return None
        
        try:
            blob_name = f"logs/{date}/{request_id}.json"
            blob_client = self.client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            if blob_client.exists():
                blob_data = blob_client.download_blob().readall()
                return json.loads(blob_data)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Blob download error: {str(e)}")
            return None


# Singleton instance
blob_service = BlobStorageService()
