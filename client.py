import os
import socket

from watchdog.observers import Observer
from watchdog.events import DirCreatedEvent, DirDeletedEvent, DirModifiedEvent, DirMovedEvent, FileClosedEvent, FileCreatedEvent, FileDeletedEvent, FileModifiedEvent, FileMovedEvent, FileOpenedEvent, FileSystemEvent, LoggingEventHandler
from watchdog.events import FileSystemEventHandler

from locker import Locker
from loggingObject import LoggingObject

class Client(FileSystemEventHandler, LoggingObject):
    """
    Client is sending changes to remote server.

    Changes are detected via watchdog library.
    """

    def __init__(self, host, port, root_dir, locker: Locker) -> None:
        FileSystemEventHandler().__init__()
        self.log_name = "CLIENT"
        self._host = host
        self._port = port
        self._root_dir = root_dir
        self._locker = locker

    def stop(self):
        """
        Stop observer
        """
        self._observer.unschedule_all()
        self._observer.stop()
        self.log("Clearing observer")

    def start(self):
        """
        Initialize observer
        """
        self._observer = Observer()
        self._observer.schedule(self, self._root_dir, recursive=True)
        self._observer.start()
        self.log(f"Client started and si connecting to {self._host}:{self._port}")
    
    def _prep_data(self, action: int, is_dir: bool, file_path: str, new_path: str, content: bytes):     
        self.log("action:", action)
        self.log("file:", file_path)
        self.log("dest:", new_path)
        data = action.to_bytes(1, "big") + is_dir.to_bytes(1, "big")
        data_cont = bytes(file_path, "utf-8") + b"\x00"
        data_cont += bytes(new_path, "utf-8") + b"\x00"
        data_cont += content
        data += len(data_cont).to_bytes(4, "big")
        data += data_cont
        return data
    
    def _read_file(self, src_path: str) -> bytes:
        """
        Return content of file as bytes.
        """
        with open(os.path.join(self._root_dir, src_path), "rb") as f:
            return f.read()

    def _send_change(self, data: bytes) -> None:
        """
        Send bytes to the server and handle response.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self._host, self._port))
            s.send(data)
            resp = s.recv(1024)
            if (resp != b"\x00"):
                self.log(f"ERROR: {resp}")
            else:
                self.log("OK")

    # Event handler methods

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        """
        Send MODIFIED command.
        """
        src_path = os.path.relpath(event.src_path, self._root_dir)
        is_dir = event.is_directory
        if (is_dir): 
            self.log(src_path, "is dir so skipping modified")
            return
        if (self._locker.is_locked(src_path)): return # file is modified by server

        data = self._prep_data(0, False, src_path, "", self._read_file(src_path))
        self._send_change(data)

    def on_created(self, event: DirCreatedEvent | FileCreatedEvent) -> None:
        """
        Send CREATED command.
        """
        src_path = os.path.relpath(event.src_path, self._root_dir)
        is_dir = event.is_directory
        if (self._locker.is_locked(src_path)): return # file is modified by server

        data = self._prep_data(1, is_dir, src_path, "", 
                              self._read_file(src_path) if not is_dir else b"")
        self._send_change(data)

    def on_moved(self, event: DirMovedEvent | FileMovedEvent) -> None:
        """
        Send MOVED command.
        """
        src_path = os.path.relpath(event.src_path, self._root_dir)
        new_path = os.path.relpath(event.dest_path, self._root_dir)
        is_dir = event.is_directory
        if (self._locker.is_locked(src_path)): return # file is modified by server
        if (self._locker.is_locked(new_path)): return # file is modified by server

        data = self._prep_data(2, is_dir, src_path, new_path, b"")
        self._send_change(data)

    def on_deleted(self, event: DirDeletedEvent | FileDeletedEvent) -> None:
        """
        Send DELETED command.
        """
        src_path = os.path.relpath(event.src_path, self._root_dir)
        is_dir = event.is_directory
        if (self._locker.is_locked(src_path)): return # file is modified by server

        data = self._prep_data(3, is_dir, src_path, "", b"")
        self._send_change(data)