import os
import socket
import shutil
from threading import Thread

from locker import Locker
from loggingObject import LoggingObject

class Server(Thread, LoggingObject):
    """
    Server accepts changes from remote client.
    """

    def __init__(self, host, port, root_dir, locker: Locker) -> None:
        super().__init__()
        self.log_name = "SERVER"
        self._host = host
        self._port = port
        self._root_dir = root_dir
        self._locker = locker
        self._listen = True

    def stop(self) -> None:
        """
        Stop server
        """
        self.ser_ins.close()

    def run(self) -> None:
        """
        Run the server until Server::stop is called
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            self.ser_ins = s
            self.ser_ins.bind((self._host, self._port))
            self.log(f"Server is listening at port {self._port} in directory {self._root_dir}")
            while True:
                self.ser_ins.listen()
                conn, addr = self.ser_ins.accept()
                with conn:
                    self.log(10*"=")
                    self.log(f"Connected by {addr}")
                    data = conn.recv(6)
                    code = data[0]
                    is_dir = data[1]
                    data_size = int.from_bytes(data[2:], "big")
                    self.log(code, is_dir, data_size)

                    data = conn.recv(data_size)
                    status = self._decode(code, is_dir, data)
                    conn.sendall(status)
                    self.log("Returning:", status, "\n")

    def _decode(self, code: int, is_dir: bool, data: bytes) -> bytes:
        self.log("Decoding")
        self.log(f"Action: {code}")
        self.log("Is directory" if is_dir else "Is file")

        data_split = data.split(b"\x00")
        if (len(data_split) < 3):
            self.log("Not enough arguments")
            return b"\x03" # not enough arguments
        
        rel_path = data_split[0].decode("utf-8")
        rel_new = data_split[1].decode("utf-8")

        self._locker.lock(rel_path)
        self._locker.lock(rel_new)

        file_path = os.path.join(self._root_dir, rel_path)
        new_path = os.path.join(self._root_dir, rel_new)
        content = data_split[2]

        ret_code = b"\x02" # unknown action
        try:
            if (code == 0):
                self._modified(file_path, content)
            elif (code == 1):
                self._created(is_dir, file_path, content)
            elif (code == 2):
                self._moved(file_path, new_path)
            elif (code == 3):
                self._deleted(is_dir, file_path)
            elif (code == 255):
                self.stop()
            ret_code = b"\x00" # success
        except Exception as e:
            self.log(e)
            ret_code = b"\x01" # unknown error
        
        self._locker.unlock(rel_new)
        self._locker.unlock(rel_path)
        return ret_code 
    
    def _modified(self, file_path: str, content: bytes) -> None:
        self.log("Modified:", file_path)
        with open(file_path, "wb") as f:
            f.write(content)
        
    def _created(self, is_dir: bool, file_path: str, content: bytes) -> None:
        if (is_dir):
            self.log("Created dir:", file_path)
            os.mkdir(file_path)
        else:
            self.log("Created file:", file_path)
            self._modified(file_path, content)
    
    def _moved(self, file_path: str, new_path: str) -> None:
        self.log("Moved:", file_path, "to:", new_path)
        path = shutil.move(file_path, new_path)
        print(path)
    
    def _deleted(self, is_dir: bool, file_path: str) -> None:
        if (is_dir):
            self.log("Deleted dir:", file_path)
            shutil.rmtree(file_path)
        else:
            self.log("Deleted file:", file_path)
            os.remove(file_path)


