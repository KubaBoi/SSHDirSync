# SocketDirSync

Every instance has server and client running at the same time.

Server accepts changes from remote machine and client sends changes from local machine to remote one.

Dependency watch dog is registered for checking changes in given directory:

`pip install watchdog`

SocketDirSync needs to be given workspace directory at the start:

`python main.py /dir/to/be/watched`

## Protocols:

| Action | Format |
| --- | --- |
| Modified | [1, 0, "file_path", 0, "new content of file"] |
| Created | [2, 0, "file_path", 0, 1(file)/2(directory), 0,  "content of file"] |
| Moved | [3, 0, "file_path", 0, "new_path", 0, 1(file)/2(directory)] |
| Deleted | [4, 0, "file_path", 0, 1(file)/2(directory)] |

