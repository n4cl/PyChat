
class MessageModel:
    def __init__(self,
                 message_id: int,
                 role: str,
                 model: str,
                 message: str = None,
                 file_id: int = None,
                 file_path: str = None,
                 file_name: str = None,
                 create_date: str = None) -> None:

        self.message_id = message_id
        self.role = role
        self.model = model
        self.message = message
        self.file_id = file_id
        self.file_path = file_path
        self.file_name = file_name
        self.create_date = create_date
