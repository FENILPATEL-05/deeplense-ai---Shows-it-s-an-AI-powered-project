import sys
import os
import gc

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

from logger import logger
from services import clip_service, qdrant_service, postgres_service


def process_image(image_path: str) -> bool:
    filename = os.path.basename(image_path)
    try:
        if postgres_service.filename_exists(filename):
            logger.info("Skipping already indexed: %s", filename)
            return True

        logger.info("Processing: %s", filename)
        embedding = clip_service.embed_image(image_path)
        
        # NEW: Automatically classify image and extract tags using CLIP
        category = clip_service.classify_image(image_path)
        tags = clip_service.extract_tags(image_path)

        payload = {
            "filename": filename,
            "path": image_path,
            "category": category,    # ✅ Now classified
            "tags": tags,            # ✅ Now extracted
        }
        qdrant_service.insert(embedding, payload)

        postgres_service.insert_image(
            filename=filename,
            path=image_path,
            category=category,       # ✅ Now classified
            tags=tags,               # ✅ Now extracted
        )

        logger.info("Successfully indexed: %s | Category: %s | Tags: %s", 
                   filename, category, tags)
        return True

    except Exception as e:
        logger.error("Failed to process %s: %s", filename, e)
        return False
    finally:
        # Force garbage collection to release file descriptors
        gc.collect()
