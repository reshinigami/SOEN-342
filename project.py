from entry import Entry
from task import Task

class Project(Entry):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)
        self.log(f'Added task: {task.title}')
    
    def search_tasks(self, keyword):
        return [task for task in self.tasks if keyword.lower() in task.title.lower()]

    def view_tasks(self):
        for task in self.tasks:
            print(f'Title: {task.title}, Description: {task.description}, Completed: {task.completed}')
    
    def to_csv(self):
        csv_data = 'Title,Description,Completed\n'
        for task in self.tasks:
            csv_data += f'"{task.title}","{task.description}",{task.completed}\n'
        return csv_data
    
    def from_csv(self, csv_data):
        lines = csv_data.strip().split('\n')[1:]  # Skip header
        for line in lines:
            title, description, completed = line.split(',')
            task = Task(title.strip('"'), description.strip('"'), completed.lower() == 'true')
            self.add_task(task)
        
