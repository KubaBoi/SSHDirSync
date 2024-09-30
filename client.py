import time
import socket

from event_handler import EventHandler

class Client:
    """
    Client is sending changes to remote server.

    Changes are detected via watchdog library.
    """

    def __init__(self, host, port, root_dir) -> None:
        self.host = host
        self.port = port
        self.root_dir = root_dir

    def init_watchdog(self):
        self.observer = EventHandler.init(self.root_dir)
    
    def prep_data(self, action: int, is_dir: bool, file_path: str, new_path: str, content: bytes):
        data = action.to_bytes(1, "big") + is_dir.to_bytes(1, "big")
        data_cont = bytes(file_path, "utf-8") + b"\x00"
        data_cont += bytes(new_path, "utf-8") + b"\x00"
        data_cont += content
        data += len(data_cont).to_bytes(4, "big")
        data += data_cont
        return data
    
    def read_file(self, src_path: str) -> bytes:
        """
        Return content of file as bytes.
        """
        with open(src_path, "r", encoding="utf-8") as f:
            return bytes(f.read(), "utf-8")

    def send_change(self, data: bytes) -> None:
        """
        Send bytes to the server and handle response.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.send(data)
            resp = s.recv(1024)
            if (resp != 0):
                print(f"ERROR: {resp}")
            else:
                print("OK")

    def send_modified(self, src_path):
        """
        Send MODIFIED command.
        """
        data = self.prep_data(0, False, src_path, "", self.read_file(src_path))
        self.send_change(data)

    def send_created(self, src_path, is_directory):
        """
        Send CREATED command.
        """
        data = self.prep_data(1, is_directory, src_path, "", 
                              self.read_file(src_path) if not is_directory else "")
        self.send_change(data)

    def send_moved(self, src_path, is_directory, new_path):
        """
        Send MOVED command.
        """
        data = self.prep_data(2, is_directory, src_path, new_path, b"")
        self.send_change(data)

    def send_deleted(self, src_path, is_directory):
        """
        Send DELETED command.
        """
        data = self.prep_data(3, is_directory, src_path, "", b"")
        self.send_change(data)