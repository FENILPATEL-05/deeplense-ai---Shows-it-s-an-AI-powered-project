import os
import logging

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from config import settings
from services import postgres_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/images", tags=["images"])


@router.get("/")
async def list_images(
    limit: int = Query(default=100, le=10000),
    offset: int = Query(default=0, ge=0),
):
    try:
        images = postgres_service.get_all_images(limit=limit, offset=offset)
        total = postgres_service.count_images()
        # Convert datetime to string for JSON serialization
        for img in images:
            if img.get("uploaded_at"):
                img["uploaded_at"] = img["uploaded_at"].isoformat() if hasattr(img["uploaded_at"], "isoformat") else str(img["uploaded_at"])
        return {"total": total, "results": images}
    except Exception as e:
        logger.error("Error listing images: %s", e)
        raise HTTPException(status_code=500, detail="Failed to list images")


@router.get("/{filename}")
async def get_image(filename: str):
    try:
        safe_filename = os.path.basename(filename)
        file_path = os.path.join(settings.IMAGES_PROCESSED_DIR, safe_filename)

        if not os.path.isfile(file_path):
            logger.warning("Image file not found: %s", safe_filename)
            raise HTTPException(status_code=404, detail=f"Image '{safe_filename}' not found")

        return FileResponse(file_path, media_type="image/jpeg")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving image: %s", e)
        raise HTTPException(status_code=500, detail="Error retrieving image")
