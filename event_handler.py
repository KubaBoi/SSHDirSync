from watchdog.observers import Observer
from watchdog.events import DirCreatedEvent, DirDeletedEvent, DirModifiedEvent, DirMovedEvent, FileCreatedEvent, FileDeletedEvent, FileModifiedEvent, FileMovedEvent, FileSystemEvent, LoggingEventHandler
from watchdog.events import FileSystemEventHandler

class EventHandler(FileSystemEventHandler):
    
    def __init__(self, client: Client) -> None:
        super().__init__()
        self.client = client

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        self.client.send_modified(event.src_path)

    def on_created(self, event: DirCreatedEvent | FileCreatedEvent) -> None:
        self.client.send_created(event.src_path, event.is_directory)

    def on_moved(self, event: DirMovedEvent | FileMovedEvent) -> None:
        self.client.send_moved(event.src_path, event.is_directory, event.dest_path)

    def on_deleted(self, event: DirDeletedEvent | FileDeletedEvent) -> None:
        self.client.send_deleted(event.src_path, event.is_directory)

    @staticmethod
    def init(path: str, client: Client) -> Observer:
        event_handler = EventHandler(client)
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()
        return observer
