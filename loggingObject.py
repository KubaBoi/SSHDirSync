
class LoggingObject:

    def __init__(self, name):
        self.log_name = name

    def log(self, *values: object):
        print(f"{self.log_name}: ", end="")
        for val in values:
            print(val, end=" ")
        print("")
