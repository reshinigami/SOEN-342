from entry import Entry

class Task(Entry):
    def __init__(self, title, description=''):
        super().__init__()
        self.title = title
        self.description = description
        self.completed = False
        self.subtasks = []

    def add_subtask(self, subtask):
        self.subtasks.append(subtask)
        self.log(f'Added subtask: {subtask.title}')

    def complete(self):
        self.completed = True
        self.log('Task completed')

class Subtask(Task):
    def __init__(self, title, description=''):
        super().__init__(title, description)