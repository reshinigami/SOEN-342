from entry import Entry
import datetime


class Task(Entry):
    def __init__(self, title, description='', priority=1, due_date=None, tags=None, project=None):
        super().__init__()

        self.title = title
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.tags = tags if tags is not None else []
        self.project = project  # Holds a Project object, or None

        self.status = "Open"
        self.creation_date = datetime.datetime.now()

        self.subtasks = []

    # Subtasks
    def add_subtask(self, subtask):
        if not isinstance(subtask, Subtask):
            raise TypeError("Only Subtask objects can be added.")
        if len(self.subtasks) >= 20:
            raise ValueError("A task cannot have more than 20 subtasks.")
        self.subtasks.append(subtask)
        self.log(f'Added subtask: {subtask.title}')

    def remove_subtask(self, subtask_title):
        for s in self.subtasks:
            if s.title == subtask_title:
                self.subtasks.remove(s)
                self.log(f'Removed subtask: {subtask_title}')
                return
        raise ValueError(f'Subtask "{subtask_title}" not found.')

    # Tags
    def add_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)
            self.log(f'Added tag: {tag}')

    def remove_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)
            self.log(f'Removed tag: {tag}')
        else:
            raise ValueError(f'Tag "{tag}" not found in task "{self.title}".')

    # Updaters
    def update_title(self, title):
        self.title = title
        self.log(f'Updated title to: {title}')

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
        self.log(f'Assigned to project: {project.name}')

    def remove_from_project(self):
        self.log(f'Removed from project: {self.project.name if self.project else "None"}')
        self.project = None

    # Status
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

    def is_open(self):
        return self.status == "Open"
    
    # Getters
    def get_title(self):
        return self.title

    def get_date_created(self):
        return self.creation_date

    def get_date_due(self):
        return self.due_date

    def get_progress(self):
        if not self.subtasks:
            return 100 if self.is_completed() else 0
        completed = sum(1 for s in self.subtasks if s.is_completed())
        return (completed / len(self.subtasks)) * 100

    def __repr__(self):
        project_name = self.project.name if self.project else None
        return f"<Task '{self.title}' | Status: {self.status} | Project: {project_name}>"


class Subtask(Task):
    def __init__(self, title, description='', collaborator=None):
        super().__init__(title, description)
        self.project = None
        self.collaborator = collaborator 
    def assign_project(self, project):
        raise Exception("Subtasks cannot be assigned to projects.")

    def add_subtask(self, subtask):
        raise Exception("Subtasks cannot have nested subtasks.")

    def __repr__(self):
        collab = self.collaborator.name if self.collaborator else None
        return f"<Subtask '{self.title}' | Status: {self.status} | Collaborator: {collab}>"


class RecurringTask(Task):
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    CUSTOM = 'custom'

    def __init__(self, title, description='', priority=1, tags=None, project=None,
                 pattern=None, weekdays=None, day_of_month=None,
                 interval_days=None, start_date=None, end_date=None):
        #To make it reoccuring, due_date is not set at initialization. Instead, occurrences are generated based on the pattern and date range.
        super().__init__(title, description, priority, due_date=None, tags=tags, project=project)

        if pattern not in (self.DAILY, self.WEEKLY, self.MONTHLY, self.CUSTOM):
            raise ValueError(f'Invalid recurrence pattern: {pattern}')

        self.pattern = pattern
        self.weekdays = weekdays or []     
        self.day_of_month = day_of_month  
        self.interval_days = interval_days
        self.start_date = start_date
        self.end_date = end_date

        self.occurrences = []
        self._generate_occurrences()

    def _generate_occurrences(self):
        if not self.start_date or not self.end_date:
            return

        self.occurrences = []
        seen_dates = set()
        current = self.start_date

        while current <= self.end_date:
            due = None

            if self.pattern == self.DAILY:
                due = current
                current += datetime.timedelta(days=1)

            elif self.pattern == self.WEEKLY:
                if current.weekday() in self.weekdays:
                    due = current
                current += datetime.timedelta(days=1)

            elif self.pattern == self.MONTHLY:
                if current.day == self.day_of_month:
                    due = current
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1, day=1)
                else:
                    current = current.replace(month=current.month + 1, day=1)
                continue
            elif self.pattern == self.CUSTOM:
                if not self.interval_days or self.interval_days <= 0:
                    raise ValueError("Custom recurrence requires a positive interval_days.")
                due = current
                current += datetime.timedelta(days=self.interval_days)
            if due and due not in seen_dates:
                seen_dates.add(due)
                occurrence = TaskOccurrence(self.title, self.description, self.priority, due, self)
                self.occurrences.append(occurrence)

    def __repr__(self):
        return f"<RecurringTask '{self.title}' | Pattern: {self.pattern} | Occurrences: {len(self.occurrences)}>"


class TaskOccurrence(Task):
    def __init__(self, title, description, priority, due_date, parent):
        super().__init__(title, description, priority, due_date=due_date)
        self.parent = parent

    def assign_project(self, project):
        raise Exception("Occurrences cannot be assigned to projects directly; assign the parent RecurringTask.")

    def __repr__(self):
        return f"<Occurrence '{self.title}' | Due: {self.due_date} | Status: {self.status}>"