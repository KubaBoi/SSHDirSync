
import socket

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    try:
        while True:
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                whole_data = b""
                data = conn.recv(1024)
                while data:
                    conn.sendall(data)
                    #print(data)
                    whole_data += data
                    data = conn.recv(1024)
                #print(whole_data.decode("utf-8"))
                print(whole_data.split(b"\x00"))
    except KeyboardInterrupt:
        print("Exiting")
        
