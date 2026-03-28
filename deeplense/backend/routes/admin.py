import os
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


class RetryResponse(BaseModel):
    success_count: int
    total_count: int
    message: str


@router.post("/retry-failed", response_model=RetryResponse)
async def retry_failed_images():
    """
    Reprocess all failed images in the failed directory.
    This endpoint attempts to reindex images that previously failed.
    """
    try:
        # Import here to avoid circular imports
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "pipeline"))
        from processor import process_image
        
        failed_dir = settings.IMAGES_FAILED_DIR
        os.makedirs(failed_dir, exist_ok=True)
        
        failed_files = [f for f in os.listdir(failed_dir) 
                       if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
        
        if not failed_files:
            return RetryResponse(
                success_count=0,
                total_count=0,
                message="No failed images to retry"
            )
        
        success_count = 0
        for filename in failed_files:
            file_path = os.path.join(failed_dir, filename)
            try:
                success = process_image(file_path)
                if success:
                    dest = os.path.join(settings.IMAGES_PROCESSED_DIR, filename)
                    os.makedirs(settings.IMAGES_PROCESSED_DIR, exist_ok=True)
                    os.rename(file_path, dest)
                    logger.info(f"Successfully retried: {filename}")
                    success_count += 1
                else:
                    logger.warning(f"Failed retry for: {filename}")
            except Exception as e:
                logger.error(f"Error retrying {filename}: {e}")
        
        return RetryResponse(
            success_count=success_count,
            total_count=len(failed_files),
            message=f"Retry complete: {success_count}/{len(failed_files)} images reprocessed"
        )
    
    except Exception as e:
        logger.error(f"Error in retry-failed endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/failed-images")
async def list_failed_images():
    """Get list of images that failed to process."""
    try:
        failed_dir = settings.IMAGES_FAILED_DIR
        os.makedirs(failed_dir, exist_ok=True)
        
        failed_files = [f for f in os.listdir(failed_dir) 
                       if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
        
        return {
            "count": len(failed_files),
            "files": failed_files
        }
    
    except Exception as e:
        logger.error(f"Error listing failed images: {e}")
        raise HTTPException(status_code=500, detail=str(e))
