import time

class Locker:

    def __init__(self) -> None:
        self.locked = []

    def lock(self, path: str) -> None:
        if (path == ""): return

        while self.is_locked(path):
            print(path, "is locked... waiting")
            time.sleep(1)
        print("locking:", path)
        self.locked.append(path)

    def unlock(self, path: str) -> None:
        if (path == ""): return

        if (not self.is_locked(path)): return
        print("unlocking:", path)
        time.sleep(1)
        self.locked.remove(path)
        print("unlocked:", path)

    def is_locked(self, path: str) -> bool:
        return path in self.locked