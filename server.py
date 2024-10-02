import os
import socket
import shutil
from threading import Thread

from locker import Locker

class Server(Thread):
    """
    Server accepts changes from remote client.
    """

    def __init__(self, host, port, root_dir, locker: Locker) -> None:
        super().__init__()
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
            print(f"Server is listening at port {self._port} in directory {self._root_dir}")
            while True:
                self.ser_ins.listen()
                conn, addr = self.ser_ins.accept()
                with conn:
                    print(f"Connected by {addr}")
                    data = conn.recv(6)
                    code = data[0]
                    is_dir = data[1]
                    data_size = int.from_bytes(data[2:], "big")
                    print(code, is_dir, data_size)

                    data = conn.recv(data_size)
                    status = self._decode(code, is_dir, data)
                    conn.sendall(status)
                    print("Returning:", status)

    def _decode(self, code: int, is_dir: bool, data: bytes) -> bytes:
        print("Decoding")
        print(f"Action: {code}")
        print("Is directory" if is_dir else "Is file")

        data_split = data.split(b"\x00")
        if (len(data_split) < 3):
            print("Not enough arguments")
            return b"\x03" # not enough arguments
        
        rel_path = data_split[0].decode("utf-8")
        rel_new = data_split[1].decode("utf-8")

        self._locker.lock(rel_path)
        self._locker.lock(rel_new)

        print(rel_path)

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
            print(e)
            ret_code = b"\x01" # unknown error
        
        self._locker.unlock(rel_new)
        self._locker.unlock(rel_path)
        return ret_code 
    
    def _modified(self, file_path: str, content: bytes) -> None:
        print("Modified:", file_path)
        with open(file_path, "wb") as f:
            f.write(content)
        
    def _created(self, is_dir: bool, file_path: str, content: bytes) -> None:
        if (is_dir):
            print("Created dir:", file_path)
            os.mkdir(file_path)
        else:
            print("Created file:", file_path)
            self._modified(file_path, content)
    
    def _moved(self, file_path: str, new_path: str) -> None:
        print("Moved:", file_path, "to:", new_path)
        shutil.move(file_path, new_path)
    
    def _deleted(self, is_dir: bool, file_path: str) -> None:
        if (is_dir):
            print("Deleted dir:", file_path)
            shutil.rmtree(file_path)
        else:
            print("Deleted file:", file_path)
            os.remove(file_path)


