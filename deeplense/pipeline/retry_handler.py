import sys
import os
import time
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

from logger import logger
from processor import process_image
from config import settings


def retry_failed_images(max_retries: int = 3, retry_delay: float = 2.0):
    """
    Reprocess all failed images in the failed directory.
    
    Args:
        max_retries: Maximum number of retry attempts per image
        retry_delay: Delay in seconds between retries
    """
    failed_dir = settings.IMAGES_FAILED_DIR
    os.makedirs(failed_dir, exist_ok=True)
    
    failed_files = [f for f in os.listdir(failed_dir) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    
    if not failed_files:
        logger.info("No failed images to retry")
        return
    
    logger.info(f"Found {len(failed_files)} failed images to retry")
    
    success_count = 0
    for filename in failed_files:
        file_path = os.path.join(failed_dir, filename)
        logger.info(f"Retrying: {filename}")
        
        # Try multiple times with delay
        for attempt in range(max_retries):
            try:
                success = process_image(file_path)
                if success:
                    # Move to processed directory
                    dest = os.path.join(settings.IMAGES_PROCESSED_DIR, filename)
                    os.makedirs(settings.IMAGES_PROCESSED_DIR, exist_ok=True)
                    os.rename(file_path, dest)
                    logger.info(f"✓ Successfully retried: {filename}")
                    success_count += 1
                    break
                else:
                    if attempt < max_retries - 1:
                        logger.warning(f"Retry {attempt + 1}/{max_retries} failed for {filename}, retrying...")
                        time.sleep(retry_delay)
                    else:
                        logger.error(f"Failed after {max_retries} attempts: {filename}")
            except Exception as e:
                logger.error(f"Error retrying {filename}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
    
    logger.info(f"Retry complete: {success_count}/{len(failed_files)} images reprocessed successfully")
    return success_count, len(failed_files)


if __name__ == "__main__":
    retry_failed_images()
