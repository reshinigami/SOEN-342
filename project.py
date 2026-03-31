from entry import Entry

class Project(Entry):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)
        self.log(f'Added task: {task.title}')
