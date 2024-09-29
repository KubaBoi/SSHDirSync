import sys
import time
from watchdog.observers import Observer
from watchdog.events import DirCreatedEvent, DirDeletedEvent, DirModifiedEvent, DirMovedEvent, FileCreatedEvent, FileDeletedEvent, FileModifiedEvent, FileMovedEvent, FileSystemEvent, LoggingEventHandler
from watchdog.events import FileSystemEventHandler

class EventHandler(FileSystemEventHandler):
    
    def __init__(self) -> None:
        super().__init__()

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        print("MODIFIED", event)

    def on_created(self, event: DirCreatedEvent | FileCreatedEvent) -> None:
        print("CREATED", event)

    def on_moved(self, event: DirMovedEvent | FileMovedEvent) -> None:
        print("MOVED", event)

    def on_deleted(self, event: DirDeletedEvent | FileDeletedEvent) -> None:
        print("DELETED", event)

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = EventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()