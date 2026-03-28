import sys
import os
import glob
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

from config import settings
from logger import logger
from processor import process_image
from services import postgres_service, qdrant_service

SUPPORTED_EXTENSIONS = ("*.jpg", "*.jpeg", "*.png", "*.webp")


def main():
    postgres_service.init_db()
    qdrant_service.create_collection_if_not_exists()

    inbox_dir = settings.IMAGES_INBOX_DIR
    processed_dir = settings.IMAGES_PROCESSED_DIR
    failed_dir = settings.IMAGES_FAILED_DIR
    os.makedirs(inbox_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(failed_dir, exist_ok=True)

    files = []
    for pattern in SUPPORTED_EXTENSIONS:
        files.extend(glob.glob(os.path.join(inbox_dir, pattern)))
        files.extend(glob.glob(os.path.join(inbox_dir, pattern.upper())))

    files = sorted(set(files))
    total = len(files)
    logger.info("Found %d images in %s", total, inbox_dir)

    if total == 0:
        logger.info("No images to index. Place images in %s and run again.", inbox_dir)
        return

    indexed = 0
    skipped = 0
    failed = 0

    for i, filepath in enumerate(files, 1):
        filename = os.path.basename(filepath)

        if postgres_service.filename_exists(filename):
            skipped += 1
            if i % 100 == 0 or i == total:
                print(f"Progress: {i}/{total} (indexed: {indexed}, skipped: {skipped}, failed: {failed})")
            continue

        success = process_image(filepath)
        if success:
            indexed += 1
            dest = os.path.join(processed_dir, filename)
            shutil.move(filepath, dest)
        else:
            failed += 1
            dest = os.path.join(failed_dir, filename)
            shutil.move(filepath, dest)

        if i % 100 == 0 or i == total:
            print(f"Progress: {i}/{total} (indexed: {indexed}, skipped: {skipped}, failed: {failed})")

    print(f"\n{'='*50}")
    print(f"Bulk indexing complete!")
    print(f"  Total files:  {total}")
    print(f"  Indexed:      {indexed}")
    print(f"  Skipped:      {skipped}")
    print(f"  Failed:       {failed}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
