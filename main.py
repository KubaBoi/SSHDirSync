import os
import sys
import threading

from locker import Locker
from client import Client
from server import Server

if __name__ == "__main__":
    loc_port = int(sys.argv[1])
    rem_port = int(sys.argv[2])

    locker = Locker()
    cli = Client("127.0.0.1", rem_port, os.getcwd(), locker)
    srv = Server("127.0.0.1", loc_port, os.getcwd(), locker)

    cli.start()
    srv.start()

    try:
        run = True
        while run:
            command = input()
            if (command == "exit"):
                run = False
    except KeyboardInterrupt as e:
        pass

    cli.stop()
    srv.stop()
    srv.join()
