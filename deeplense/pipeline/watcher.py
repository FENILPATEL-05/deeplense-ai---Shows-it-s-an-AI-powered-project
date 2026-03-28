import sys
import os
import time
import shutil
import gc
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from config import settings
from logger import logger
from processor import process_image

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
RETRY_DELAY_HOURS = 2  # Retry failed images after 2 hours


class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        ext = os.path.splitext(event.src_path)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            return

        time.sleep(0.5)

        filename = os.path.basename(event.src_path)
        logger.info("New file detected: %s", filename)

        success = process_image(event.src_path)

        if success:
            dest = os.path.join(settings.IMAGES_PROCESSED_DIR, filename)
            if os.path.abspath(event.src_path) != os.path.abspath(dest):
                shutil.move(event.src_path, dest)
            logger.info("Moved to processed: %s", filename)
        else:
            dest = os.path.join(settings.IMAGES_FAILED_DIR, filename)
            shutil.move(event.src_path, dest)
            logger.error("Moved to failed: %s", filename)


def auto_retry_failed_images():
    """
    Automatically retry failed images that haven't been modified in RETRY_DELAY_HOURS.
    This prevents hammering services with immediate retries.
    """
    failed_dir = settings.IMAGES_FAILED_DIR
    os.makedirs(failed_dir, exist_ok=True)
    
    now = time.time()
    cutoff_time = now - (RETRY_DELAY_HOURS * 3600)
    
    failed_files = [f for f in os.listdir(failed_dir) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    
    if not failed_files:
        return
    
    retry_count = 0
    for filename in failed_files:
        file_path = os.path.join(failed_dir, filename)
        try:
            # Only retry if file hasn't been modified recently
            file_mtime = os.path.getmtime(file_path)
            if file_mtime < cutoff_time:
                logger.info("Auto-retrying failed image: %s", filename)
                success = process_image(file_path)
                if success:
                    dest = os.path.join(settings.IMAGES_PROCESSED_DIR, filename)
                    os.makedirs(settings.IMAGES_PROCESSED_DIR, exist_ok=True)
                    os.rename(file_path, dest)
                    logger.info("✓ Auto-retry successful: %s", filename)
                    retry_count += 1
                else:
                    logger.warning("Auto-retry failed: %s (will try again in %d hours)", filename, RETRY_DELAY_HOURS)
        except Exception as e:
            logger.error("Error auto-retrying %s: %s", filename, e)
    
    if retry_count > 0:
        logger.info("Auto-retry completed: %d images recovered", retry_count)


def main():
    watch_dir = settings.IMAGES_INBOX_DIR
    os.makedirs(watch_dir, exist_ok=True)
    os.makedirs(settings.IMAGES_PROCESSED_DIR, exist_ok=True)
    os.makedirs(settings.IMAGES_FAILED_DIR, exist_ok=True)

    logger.info("Watching directory: %s", watch_dir)
    logger.info("Failed images will auto-retry after %d hours", RETRY_DELAY_HOURS)

    event_handler = ImageHandler()
    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=False)
    observer.start()

    try:
        gc_counter = 0
        retry_counter = 0
        
        while True:
            time.sleep(1)
            
            # Run garbage collection every 30 seconds
            gc_counter += 1
            if gc_counter >= 30:
                gc.collect()
                gc_counter = 0
            
            # Run auto-retry check every hour (3600 seconds)
            retry_counter += 1
            if retry_counter >= 3600:
                auto_retry_failed_images()
                retry_counter = 0
                
    except KeyboardInterrupt:
        logger.info("Stopping watcher...")
        observer.stop()
    finally:
        observer.join()
        gc.collect()
        logger.info("Watcher stopped.")


if __name__ == "__main__":
    main()
