import threading
import socket

from client import Client
from server import Server

if __name__ == "__main__":
    cli = Client("127.0.0.1", 65432)
    srv = Server("127.0.0.1", 65432)

    cli.init_watchdog()
    cli.