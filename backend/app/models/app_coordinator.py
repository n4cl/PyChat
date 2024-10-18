
class AppMessage:
    def __init__(self, message: str, file: str="", file_name: str="") -> None:
        self.message = message
        self.file = file
        self.file_name = file_name
