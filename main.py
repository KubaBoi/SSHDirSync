from client import Client

cli = Client("127.0.0.1", 65432)
cli.send_modified("README.md")