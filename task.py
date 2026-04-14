from entry import Entry
import datetime


class Task(Entry):
    def __init__(self, title, description='', priority=1, due_date=None, tags=None, project=None):
        super().__init__()
        
        # Core fields
        self.title = title
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.tags = tags if tags is not None else []
        self.project = project
        
        # State
        self.status = "Open" 
        self.creation_date = datetime.datetime.now()
        
        # Structure
        self.subtasks = []

    # ---------- Subtasks ----------
    def add_subtask(self, subtask):
        if not isinstance(subtask, Subtask):
            raise TypeError("Only Subtask objects can be added")
        
        self.subtasks.append(subtask)
        self.log(f'Added subtask: {subtask.title}')

    # ---------- Tags ----------
    def add_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)
            self.log(f'Added tag: {tag}')

    def remove_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)
            self.log(f'Removed tag: {tag}')
        else:
            print(f'Tag "{tag}" not found in task "{self.title}".')

    # ---------- Updates ----------
    def update_description(self, description):
        self.description = description
        self.log('Updated description')

    def update_priority(self, priority):
        self.priority = priority
        self.log(f'Updated priority to {priority}')

    def update_due_date(self, due_date):
        self.due_date = due_date
        self.log(f'Updated due date to {due_date}')

    def assign_project(self, project):
        self.project = project
        self.log(f'Assigned to project: {project}')

    def remove_from_project(self):
        self.log(f'Removed from project: {self.project}')
        self.project = None

    # ---------- Status ----------
    def complete(self):
        self.status = "Completed"
        self.log('Task completed')

    def cancel(self):
        self.status = "Cancelled"
        self.log('Task cancelled')

    def reopen(self):
        self.status = "Open"
        self.log('Task reopened')

    def is_completed(self):
        return self.status == "Completed"

    # ---------- Getters ----------
    def get_title(self):
        return self.title

    def get_date_created(self):
        return self.creation_date

    def get_date_due(self):
        return self.due_date

    # ---------- Progress ----------
    def get_progress(self):
        if not self.subtasks:
            return 100 if self.is_completed() else 0

        completed = sum(1 for s in self.subtasks if s.is_completed())
        return (completed / len(self.subtasks)) * 100

    # ---------- Representation ----------
    def __repr__(self):
        return f"<Task '{self.title}' | Status: {self.status} | Project: {self.project}>"



class Subtask(Task):
    def __init__(self, title, description=''):
        super().__init__(title, description)
        
        # Subtasks should NOT belong to projects
        self.project = None

    def assign_project(self, project):
        raise Exception("Subtasks cannot be assigned to projects")