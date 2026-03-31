from datetime import datetime

class Entry:
    def __init__(self):
        self.created_at = datetime.now()
        self.history = []

    def log(self, action):
        self.history.append((datetime.now(), action))