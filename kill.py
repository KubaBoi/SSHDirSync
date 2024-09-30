import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(("127.0.0.1", 65432))
    print("Killing")
    s.send(b"\xff\x01\x00\x00\x00\x03\x00\x00\x00")
    print(s.recv(1))