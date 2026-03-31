class TaskManager:
    def __init__(self):
        self.projects = []

    def add_project(self, project):
        self.projects.append(project)
        print(f'Added project: {project.name}')