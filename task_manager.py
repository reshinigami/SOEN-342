from task import Task
import datetime


class history():
    def __init__(self):
        self.history = {'Task-Name': [], 'Activity': [], 'Timestamp': []}
    
    def log(self, action, task_name):
        self.history['Task-Name'].append(task_name)
        self.history['Activity'].append((datetime.datetime.now(), action))
        self.history['Timestamp'].append(datetime.datetime.now())
    
    def get_history(self):
        return self.history


class TaskManager:
    def __init__(self):
        self.projects = []
        self.history = history()
        self.tasks = [] 
        
    def add_project(self, project):
        self.projects.append(project)
        print(f'Added project: {project.name}')
    
    def get_projects(self):
        return self.projects
    

    
    def create_task(self, title, description='', priority=1, due_date=None, tags=None):
        task = Task(title, description, priority, due_date, tags)
        self.tasks.append(task)
        self.history.log('Created task', title)
        return task
    def complete_task(self, task_title):
        task = self.get_task(task_title)
        if task:
            task.complete()
            self.history.log('Completed task', task_title)
        else:
            print(f'Task "{task_title}" not found.')
    
    def cancel_task(self, task_title):
        task = self.get_task(task_title)
        if task:
            task.cancel()
            self.history.log('Cancelled task', task_title)
        else:
            print(f'Task "{task_title}" not found.')
    
    def update_task(self, task_title, description=None, priority=None, due_date=None):
        task = self.get_task(task_title)
        if task:
            if description is not None:
                task.update_description(description)
                self.history.log('Updated description', task_title)
            if priority is not None:
                task.update_priority(priority)
                self.history.log(f'Updated priority to {priority}', task_title)
            if due_date is not None:
                task.update_due_date(due_date)
                self.history.log(f'Updated due date to {due_date}', task_title)
        else:
            print(f'Task "{task_title}" not found.')



    def get_task(self, task_title):
        for task in self.tasks:
            if task.title == task_title:
                return task
        return None
    
    
    def get_project_by_name(self, name):
        for project in self.projects:
            if project.name == name:
                return project
        return None

    def add_task_to_project(self, project_name, task):
        project = self.get_project_by_name(project_name)

        if not project:
            print(f'Project "{project_name}" not found.')
            return

        if task not in self.tasks:
            self.tasks.append(task)

        task.assign_project(project_name) 

    def remove_task_from_project(self, project_name, task_title):
        task = self.get_task(task_title)

        if task and task.project == project_name:
            task.remove_from_project()
        else:
            print(f'Task "{task_title}" not found in project "{project_name}".')

    def move_task(self, task_title, from_project_name, to_project_name):
        task = self.get_task(task_title)

        if not task:
            print(f'Task "{task_title}" not found.')
            return

        if task.project != from_project_name:
            print(f'Task "{task_title}" is not in "{from_project_name}".')
            return

        if not self.get_project_by_name(to_project_name):
            print(f'Project "{to_project_name}" not found.')
            return

        task.assign_project(to_project_name)
    def get_tasks_by_project(self, project_name):
        return [t for t in self.tasks if t.project == project_name]

    def search_tasks(self, keyword):
        return [
            t for t in self.tasks
            if keyword.lower() in t.title.lower() or keyword.lower() in t.description.lower()
        ]

    def view_all_tasks(self, sort_by=None):
        tasks = self.tasks.copy()

        if sort_by == 'priority':
            tasks.sort(key=lambda x: x.priority)
        elif sort_by == 'due_date':
            tasks.sort(key=lambda x: x.due_date if x.due_date else datetime.datetime.max)
        elif sort_by == 'creation_date':
            tasks.sort(key=lambda x: x.creation_date)
        elif sort_by == 'status':
            tasks.sort(key=lambda x: x.status)

        return tasks
    


    def project_to_csv(self, project_name):
        tasks = self.get_tasks_by_project(project_name)

        csv_data = 'Title,Description,Status\n'
        for t in tasks:
            csv_data += f'"{t.title}","{t.description}","{t.status}"\n'

        return csv_data



    def project_from_csv(self, project_name, csv_data):
        project = self.get_project_by_name(project_name)

        if not project:
            print(f'Project "{project_name}" not found.')
            return

        lines = csv_data.strip().split('\n')[1:]

        for line in lines:
            title, description, status = line.split(',')

            task = Task(
                title.strip('"'),
                description.strip('"')
            )

            task.status = status.strip('"')
            task.assign_project(project_name)

            self.tasks.append(task)