from datetime import datetime


class Entry:
    def __init__(self):
        self.created_at = datetime.now()
        self.history = []

    def log(self, action):
        self.history.append((datetime.now(), action))

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

class Project(Entry):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)
        self.log(f'Added task: {task.title}')

class TaskManager:
    def __init__(self):
        self.projects = []

    def add_project(self, project):
        self.projects.append(project)
        print(f'Added project: {project.name}')

