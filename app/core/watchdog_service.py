import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.utils.logger import setup_logger
from app.config import INPUT_DIR

logger = setup_logger("Watchdog")

class FileEventHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_created(self, event):
        if not event.is_directory:
            logger.info(f"New file detected: {event.src_path}")
            self.callback(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            logger.info(f"File deleted: {event.src_path}")

class WatchdogService:
    def __init__(self, process_callback):
        self.observer = Observer()
        self.handler = FileEventHandler(process_callback)
        self.directory = INPUT_DIR
        self.is_running = False

    def start(self):
        if not self.is_running:
            if not os.path.exists(self.directory):
                os.makedirs(self.directory)
            self.observer.schedule(self.handler, self.directory, recursive=False)
            self.observer.start()
            self.is_running = True
            logger.info(f"Watchdog started monitoring: {self.directory}")

    def stop(self):
        if self.is_running:
            self.observer.stop()
            self.observer.join()
            self.is_running = False
            logger.info("Watchdog stopped.")

_service_instance = None

def get_watchdog_service(callback=None):
    global _service_instance
    if _service_instance is None and callback:
        _service_instance = WatchdogService(callback)
    return _service_instance
