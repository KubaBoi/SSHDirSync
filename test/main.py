import os
import sys

from locker import Locker
from client import Client
from server import Server

if __name__ == "__main__":
    loc_port = int(sys.argv[1]) if len(sys.argv) > 1 else 65432
    rem_port = int(sys.argv[2]) if len(sys.argv) > 2 else 65433
    dir_root = os.getcwd()
    if (len(sys.argv) > 3):
        dir_root = os.path.join(dir_root, "test")

    locker = Locker()
    cli = Client("127.0.0.1", rem_port, dir_root, locker)
    srv = Server("127.0.0.1", loc_port, dir_root, locker)

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
