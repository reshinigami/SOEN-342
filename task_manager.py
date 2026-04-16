from task import Task, Subtask, RecurringTask
from project import Project, Collaborator
from icalendar import Calendar, Event

import datetime
import csv
import io


class History:
    def __init__(self):
        self.entries = []

    def log(self, task_name, action):
        self.entries.append((datetime.datetime.now(), task_name, action))

    def get_history(self):
        return self.entries


class TaskManager:
    def __init__(self):
        self.projects = []
        self.tasks = []    
        self.history = History()

    def add_project(self, project):
        if not isinstance(project, Project):
            raise TypeError("Only Project objects can be added.")
        for p in self.projects:
            if p.name == project.name:
                raise ValueError(f'Project "{project.name}" already exists.')
        self.projects.append(project)
        self.history.log(project.name, 'Created project')

    def get_project_by_name(self, name):
        for p in self.projects:
            if p.name == name:
                return p
        return None

    def get_projects(self):
        return self.projects

    def add_collaborator_to_project(self, project_name, collaborator):
        project = self._require_project(project_name)
        project.add_collaborator(collaborator)

    def assign_collaborator_to_task(self, task_title, collaborator):
        task = self._require_task(task_title)

        open_count = self._count_open_tasks_for_collaborator(collaborator)
        limit = collaborator.get_limit()
        if open_count >= limit:
            raise ValueError(
                f'Collaborator "{collaborator.name}" ({collaborator.category()}) '
                f'already has {open_count} open tasks (limit: {limit}). '
                f'They must complete at least one before being assigned a new task.'
            )
        subtask = Subtask(
            title=f'{task.title} [{collaborator.name}]',
            description=f'Subtask assigned to {collaborator.name}',
            collaborator=collaborator
        )
        task.add_subtask(subtask)
        self.history.log(task_title, f'Assigned collaborator {collaborator.name}')

    def _count_open_tasks_for_collaborator(self, collaborator):
        count = 0
        for task in self.tasks:
            for subtask in task.subtasks:
                if subtask.collaborator == collaborator and subtask.is_open():
                    count += 1
        return count

    def list_overloaded_collaborators(self):
        """Returns a list of (collaborator, open_count, limit) for overloaded collaborators."""
        overloaded = []
        seen = set()

        for project in self.projects:
            for collaborator in project.collaborators:
                if id(collaborator) in seen:
                    continue
                seen.add(id(collaborator))

                open_count = self._count_open_tasks_for_collaborator(collaborator)
                limit = collaborator.get_limit()
                if open_count > limit:
                    overloaded.append((collaborator, open_count, limit))

        return overloaded
    def create_task(self, title, description='', priority=1, due_date=None, tags=None):
        # OCL: no more than 50 open tasks without a due date
        if due_date is None:
            open_no_due = sum(
                1 for t in self.tasks if t.is_open() and t.due_date is None
            )
            if open_no_due >= 50:
                raise ValueError(
                    "Cannot create task: the system already has 50 open tasks without a due date."
                )

        task = Task(title, description, priority, due_date, tags)
        self.tasks.append(task)
        self.history.log(title, 'Created task')
        return task

    def create_recurring_task(self, title, description='', priority=1, tags=None,
                               project_name=None, pattern=None, weekdays=None,
                               day_of_month=None, interval_days=None,
                               start_date=None, end_date=None):
        project = self.get_project_by_name(project_name) if project_name else None

        task = RecurringTask(
            title=title, description=description, priority=priority,
            tags=tags, project=project, pattern=pattern, weekdays=weekdays,
            day_of_month=day_of_month, interval_days=interval_days,
            start_date=start_date, end_date=end_date
        )
        self.tasks.append(task)
        self.history.log(title, f'Created recurring task ({pattern})')
        return task


    def complete_task(self, task_title):
        task = self._require_task(task_title)
        task.complete()
        self.history.log(task_title, 'Completed task')

    def cancel_task(self, task_title):
        task = self._require_task(task_title)
        task.cancel()
        self.history.log(task_title, 'Cancelled task')

    def reopen_task(self, task_title):
        task = self._require_task(task_title)
        if task.due_date is None:
            open_no_due = sum(
                1 for t in self.tasks if t.is_open() and t.due_date is None
            )
            if open_no_due >= 50:
                raise ValueError(
                    "Cannot reopen task: the system already has 50 open tasks without a due date."
                )
        for subtask in task.subtasks:
            if subtask.collaborator:
                collaborator = subtask.collaborator
                open_count = self._count_open_tasks_for_collaborator(collaborator)
                limit = collaborator.get_limit()
                if open_count >= limit:
                    raise ValueError(
                        f'Cannot reopen: collaborator "{collaborator.name}" '
                        f'({collaborator.category()}) would exceed their limit of {limit} open tasks.'
                    )
        task.reopen()
        self.history.log(task_title, 'Reopened task')

    def update_task(self, task_title, title=None, description=None, priority=None,
                    due_date=None, tags_to_add=None, tags_to_remove=None):
        task = self._require_task(task_title)
        if title is not None:
            task.update_title(title)
            self.history.log(task_title, f'Updated title to {title}')
        if description is not None:
            task.update_description(description)
            self.history.log(task_title, 'Updated description')
        if priority is not None:
            task.update_priority(priority)
            self.history.log(task_title, f'Updated priority to {priority}')
        if due_date is not None:
            task.update_due_date(due_date)
            self.history.log(task_title, f'Updated due date to {due_date}')
        if tags_to_add:
            for tag in tags_to_add:
                task.add_tag(tag)
        if tags_to_remove:
            for tag in tags_to_remove:
                task.remove_tag(tag)

    def add_task_to_project(self, project_name, task):
        project = self._require_project(project_name)
        if task not in self.tasks:
            self.tasks.append(task)
        task.assign_project(project)
        self.history.log(task.title, f'Assigned to project {project_name}')

    def remove_task_from_project(self, task_title):
        task = self._require_task(task_title)
        task.remove_from_project()
        self.history.log(task_title, 'Removed from project')

    def move_task(self, task_title, to_project_name):
        task = self._require_task(task_title)
        project = self._require_project(to_project_name)
        task.assign_project(project)
        self.history.log(task_title, f'Moved to project {to_project_name}')

    def get_task(self, task_title):
        for task in self.tasks:
            if task.title == task_title:
                return task
        return None

    def get_tasks_by_project(self, project_name):
        return [t for t in self.tasks if t.project and t.project.name == project_name]

    def get_tasks_by_tag(self, tag):
        return [t for t in self.tasks if tag in t.tags]

    def search_tasks(self, keyword=None, status=None, tag=None, project_name=None,
                     due_after=None, due_before=None, day_of_week=None):
        results = self.tasks.copy()

        if keyword:
            kw = keyword.lower()
            results = [t for t in results if kw in t.title.lower() or kw in t.description.lower()]
        if status:
            results = [t for t in results if t.status == status]
        if tag:
            results = [t for t in results if tag in t.tags]
        if project_name:
            results = [t for t in results if t.project and t.project.name == project_name]
        if due_after:
            results = [t for t in results if t.due_date and t.due_date >= due_after]
        if due_before:
            results = [t for t in results if t.due_date and t.due_date <= due_before]
        if day_of_week is not None:
            results = [t for t in results if t.due_date and t.due_date.weekday() == day_of_week]

        no_criteria = not any([keyword, status, tag, project_name, due_after, due_before, day_of_week is not None])
        if no_criteria:
            results = [t for t in results if t.is_open()]

        results.sort(key=lambda t: (t.due_date is None, t.due_date or datetime.datetime.max))
        return results

    def view_all_tasks(self, sort_by=None):
        tasks = self.tasks.copy()
        if sort_by == 'priority':
            tasks.sort(key=lambda x: x.priority)
        elif sort_by == 'due_date':
            tasks.sort(key=lambda x: (x.due_date is None, x.due_date or datetime.datetime.max))
        elif sort_by == 'creation_date':
            tasks.sort(key=lambda x: x.creation_date)
        elif sort_by == 'status':
            tasks.sort(key=lambda x: x.status)
        return tasks
    
    def export_to_csv(self, tasks=None):
        if tasks is None:
            tasks = self.tasks

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'TaskName', 'Description', 'Subtask', 'Status', 'Priority',
            'DueDate', 'ProjectName', 'ProjectDescription', 'Collaborator', 'CollaboratorCategory'])
        for t in tasks:
            project_name = t.project.name if t.project else('')
            project_desc = t.project.description if t.project else('')
            due = t.due_date.strftime('%Y-%m-%d') if t.due_date else('')

            if t.subtasks:
                for subtask in t.subtasks:
                    collab_name = subtask.collaborator.name if subtask.collaborator else('')
                    collab_cat = subtask.collaborator.category() if subtask.collaborator else('')
                    writer.writerow([
                        t.title, t.description, subtask.title, t.status,t.priority, due, project_name, project_desc,
                        collab_name, collab_cat])
            else:
                writer.writerow([
                    t.title, t.description, '', t.status,
                    t.priority, due, project_name, project_desc, '', ''
                ])

        return output.getvalue()
    
    def import_from_csv(self, csv_data):
        reader = csv.DictReader(io.StringIO(csv_data))

        for row in reader:
            task_title = row['TaskName'].strip()
            description = row['Description'].strip()
            status = row['Status'].strip()
            priority = int(row['Priority']) if row['Priority'].strip() else 1
            due_date_str = row['DueDate'].strip()
            project_name = row['ProjectName'].strip()
            project_desc = row['ProjectDescription'].strip()
            subtask_title = row['Subtask'].strip()
            collab_name = row['Collaborator'].strip()
            collab_cat = row['CollaboratorCategory'].strip()
            due_date = None


            if due_date_str:
                due_date = datetime.datetime.strptime(due_date_str, '%Y-%m-%d')
            project = None
            if project_name:
                project = self.get_project_by_name(project_name)
                if not project:
                    project = Project(project_name, project_desc)
                    self.add_project(project)
            task = self.get_task(task_title)
            if not task:
                task = Task(task_title, description, priority, due_date)
                task.status = status
                if project:
                    task.assign_project(project)
                self.tasks.append(task)
            if subtask_title and collab_name and project:
                collaborator = project.get_collaborator_by_name(collab_name)
                if not collaborator:
                    collaborator = _make_collaborator(collab_name, collab_cat)
                    project.add_collaborator(collaborator)

                # Only add subtask if not already present
                existing_titles = [s.title for s in task.subtasks]
                if subtask_title not in existing_titles:
                    subtask = Subtask(subtask_title, collaborator=collaborator)
                    task.add_subtask(subtask)
    def _require_task(self, task_title):
        task = self.get_task(task_title)
        if not task:
            raise ValueError(f'Task "{task_title}" not found.')
        return task

    def _require_project(self, project_name):
        project = self.get_project_by_name(project_name)
        if not project:
            raise ValueError(f'Project "{project_name}" not found.')
        return project


def _make_collaborator(name, category):
    from project import Junior_Collaborator, Intermediate_Collaborator, Senior_Collaborator
    cat = category.strip().lower()
    if cat == 'junior':
        return Junior_Collaborator(name)
    elif cat == 'intermediate':
        return Intermediate_Collaborator(name)
    elif cat == 'senior':
        return Senior_Collaborator(name)
    else:
        raise ValueError(f'Unknown collaborator category: "{category}"')
    





def export_to_ical(self, tasks=None):
    if tasks is None:
        tasks = self.tasks

    cal = Calendar()
    cal.add('prodid', '-//TaskManager//')
    cal.add('version', '2.0')

    for task in tasks:
        if isinstance(task, Task) and not isinstance(task, RecurringTask):
            if not task.due_date:
                continue

            event = Event()
            event.add('summary', task.title)
            event.add('description', task.description)
            event.add('dtstart', task.due_date)
            event.add('dtend', task.due_date + datetime.timedelta(hours=1))

            cal.add_component(event)
        elif isinstance(task, RecurringTask):

            event = Event()
            event.add('summary', task.title)
            event.add('description', task.description)

            if task.start_date:
                event.add('dtstart', task.start_date)

            # RRULE mapping
            if task.pattern == RecurringTask.DAILY:
                event.add('rrule', {'freq': 'daily'})

            elif task.pattern == RecurringTask.WEEKLY:
                event.add('rrule', {
                    'freq': 'weekly',
                    'byday': [ ['MO','TU','WE','TH','FR','SA','SU'][d] for d in task.weekdays ]
                })


            elif task.pattern == RecurringTask.MONTHLY:
                event.add('rrule', {
                    'freq': 'monthly',
                    'bymonthday': task.day_of_month
                })
            elif task.pattern == RecurringTask.CUSTOM:
                event.add('rrule', {
                    'freq': 'daily',
                    'interval': task.interval_days
                })

            cal.add_component(event)
    return cal.to_ical().decode('utf-8')