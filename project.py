from entry import Entry

class Project(Entry):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __repr__(self):
        project_name = self.project.name if self.project else None
        return f"<Task '{self.title}' | Status: {self.status} | Project: {project_name}>"