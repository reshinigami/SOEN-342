from task_manager import TaskManager
from project import Project
from task import Task, Subtask

def main():
    manager = TaskManager()
    project1 = Project('temp')
    manager.add_project(project1)

    task1 = Task('Do stuff, maybe finihs assignemtn', 'Complete the task management system')
    task2 = Task('Finish the artifact stuff', 'Like UML diagram, Sequence diagrams, etc.')
    project1.add_task(task1)
    project1.add_task(task2)

main()