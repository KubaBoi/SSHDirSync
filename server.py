import os
import socket
import shutil

class Server:

    def __init__(self, host, port, root_dir) -> None:
        self.host = host
        self.port = port
        self.root_dir = root_dir
        self.listen = True

    def stop(self) -> None:
        self.listen = False

    def run(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            print(f"Server is listening at port {self.port} in directory {self.root_dir}")
            while self.listen:
                s.listen()
                conn, addr = s.accept()
                with conn:
                    print(f"Connected by {addr}")
                    data = conn.recv(6)
                    code = data[0]
                    is_dir = data[1]
                    data_size = int.from_bytes(data[2:], "big")
                    print(code, is_dir, data_size)

                    data = conn.recv(data_size)
                    print(data)
                    conn.sendall(self.decode(code, is_dir, data))

    def decode(self, code: int, is_dir: bool, data: bytes) -> bytes:
        print("Decoding")
        print(f"Action: {code}")
        print("Is directory" if is_dir else "Is file")

        data_split = data.split(b"\x00")
        if (len(data_split) < 3):
            return b"\x03" # not enough arguments
        
        file_path = os.path.join(self.root_dir, data_split[0])
        new_path = os.path.join(self.root_dir, data_split[1])
        content = data_split[2]

        try:
            if (code == 0):
                return self.modified(file_path, content)
            elif (code == 1):
                return self.created(is_dir, file_path, content)
            elif (code == 2):
                return self.moved(file_path, new_path)
            elif (code == 3):
                return self.deleted(is_dir, file_path)
            elif (code == 255):
                self.stop()
                return b"\x00"
        except Exception as e:
            print(e)
            return b"\x01" # unknown error
        return b"\x02" # unknown action
    
    def modified(self, file_path: str, content: str) -> bytes:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return b"\x00"
        
    def created(self, is_dir: bool, file_path: str, content: str) -> bytes:
        if (is_dir):
            os.mkdir(file_path)
        else:
            return self.modified(file_path, content)
        return b"\x00"
    
    def moved(self, file_path: str, new_path: str) -> bytes:
        shutil.move(file_path, new_path)
        return b"\x00"
    
    def deleted(self, is_dir: bool, file_path: str) -> bytes:
        if (is_dir):
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)
        return b"\x00"

if __name__ == "__main__":
    srv = Server("127.0.0.1", 65432, os.getcwd())
    srv.run()


