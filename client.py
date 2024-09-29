import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

class Client:

    def __init__(self, host, port) -> None:
        self.host = host
        self.port = port

    def prep_header(self, type, src_path) -> bytes:
        data = type + "\x00"
        data += bytes(src_path, "utf-8")
        data += b"\x00"
        return data
    
    def prep_data(self, data):
        ret = data[0]
        for item in data[1:]:
            ret += b"\x00"
            if (type)
    
    def read_file(self, src_path) -> bytes:
        with open(src_path, "r", encoding="utf-8") as f:
            return bytes(f.read(), "utf-8")

    def send_change(self, data) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.send(data)
            s.recv(1024)

    def send_modified(self, src_path):
        data = self.prep_header(b"\x01", src_path)
        data += self.read_file(src_path)
        self.send_change(data)

    def send_created(self, src_path, is_directory):
        data = self.prep_header(b"\x02", src_path)
        data += (b"\x02" if is_directory else b"\x01") + b"\x00"
        data += self.read_file(src_path)
        self.send_change(data)

    def send_moved(self, src_path, new_path, is_directory):
        data = self.prep_header(b"\x03", src_path)
        data += bytes(new_path, "utf-8")
        data += b"\x00" + (b"\x02" if is_directory else b"\x01") + b"\x00"
        self.send_change(data)