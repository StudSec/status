from .common import WebService

class Google(WebService):
    def __init__(self):
        super().__init__()
        self.uuid = "80099d62-dc68-468d-b50e-f1b5910d011b"
        self.url = "https://google.com/"
        self.name = "Google"
        self.status = "up"