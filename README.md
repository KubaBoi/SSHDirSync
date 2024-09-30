# SocketDirSync

Every instance has server and client running at the same time.

Server accepts changes from remote machine and client sends changes from local machine to remote one.

Dependency watch dog is registered for checking changes in given directory:

`pip install watchdog`

SocketDirSync needs to be given workspace directory at the start:

`python main.py /dir/to/be/watched`

## Protocols:

Numbers in brackets are byte counts:

[action (1), is_directory (1), size of content (4) , "file_path", 0, "new_path", 0, "content of file"]

| Action | Code |
| --- | --- |
| Modified | 0 |
| Created | 1 |
| Moved | 2 |
| Deleted | 3 |
| Kill | 255 |

Responses:

```
== 0 - OK
> 0 - FAIL 

1 - unknown error
2 - unknown action
3 - not enough arguments 
```