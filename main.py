from task_manager import TaskManager
from project import Project, Junior_Collaborator, Intermediate_Collaborator, Senior_Collaborator
import datetime


def section(title):
    print(f"\n--- {title} ---")


def test(label, fn):
    try:
        result = fn()
        print(f"[OK] {label}")
        if result is not None:
            print(f"     {result}")
    except Exception as e:
        print(f"[ERR] {label} -> {e}")


if __name__ == "__main__":
    tm = TaskManager()

    #test project objects
    section("Projects")
    p1 = Project("Course Assignments", "All university work")
    p2 = Project("Home Renovation", "Fix the kitchen and bathroom")

    def add_p1(): return tm.add_project(p1)
    def add_p2(): return tm.add_project(p2)
    def dup_project(): return tm.add_project(Project("Course Assignments"))
    def get_proj(): return tm.get_project_by_name("Course Assignments")

    test("Add Course Assignments", add_p1)
    test("Add Home Renovation", add_p2)
    test("Duplicate project fails", dup_project)
    test("Find project by name", get_proj)
    test("List projects", tm.get_projects)
    #Test collaborators
    section("Collaborators")

    alice = Junior_Collaborator("Alice")
    bob   = Intermediate_Collaborator("Bob")
    carol = Senior_Collaborator("Carol")

    def add_alice(): return tm.add_collaborator_to_project("Course Assignments", alice)
    def add_bob(): return tm.add_collaborator_to_project("Course Assignments", bob)
    def add_carol(): return tm.add_collaborator_to_project("Home Renovation", carol)
    def dup_collab(): return tm.add_collaborator_to_project("Course Assignments", alice)
    def bad_collab(): return tm.add_collaborator_to_project("Course Assignments", "Fake")
    test("Add Alice", add_alice)
    test("Add Bob", add_bob)
    test("Add Carol", add_carol)
    test("Duplicate collaborator fails", dup_collab)
    test("Reject invalid collaborator", bad_collab)

    #Task object tests
    section("Tasks")
    today = datetime.datetime.now()
    next_week = today + datetime.timedelta(days=7)

    def create_lab():
        return tm.create_task("Lab Report", "Write experiment", priority=2,
                              due_date=next_week, tags=["school"])
    def create_simple():
        return tm.create_task("Buy groceries", priority=1)
    def create_midterm():
        t = tm.create_task("Midterm Study", "Study", priority=3, due_date=next_week)
        return tm.add_task_to_project("Course Assignments", t)
    test("Create task with due date", create_lab)
    test("Create simple task", create_simple)
    test("Create + assign task", create_midterm)
    lab = tm.get_task("Lab Report")
    def assign_lab(): return tm.add_task_to_project("Course Assignments", lab)
    def rename_lab(): return tm.update_task("Lab Report", title="Lab Report Final")
    def update_priority(): return tm.update_task("Lab Report Final", priority=3)
    def add_tag(): return tm.update_task("Lab Report Final", tags_to_add=["urgent"])
    def remove_tag(): return tm.update_task("Lab Report Final", tags_to_remove=["urgent"])
    test("Assign task to project", assign_lab)
    test("Rename task", rename_lab)
    test("Update priority", update_priority)
    test("Add tag", add_tag)
    test("Remove tag", remove_tag)
    test("Get task", lambda: tm.get_task("Lab Report Final"))
    test("Tasks by project", lambda: tm.get_tasks_by_project("Course Assignments"))
    test("Tasks by tag", lambda: tm.get_tasks_by_tag("school"))

    #subtask checks
    section("Subtasks")

    midterm = tm.get_task("Midterm Study")
    def assign_alice(): return tm.assign_collaborator_to_task("Midterm Study", alice)
    def assign_bob(): return tm.assign_collaborator_to_task("Midterm Study", bob)
    test("Assign Alice", assign_alice)
    test("Assign Bob", assign_bob)
    test("View subtasks", lambda: midterm.subtasks)
    test("Progress", lambda: f"{midterm.get_progress():.0f}%")

    #status chages check
    section("Task lifecycle")
    test("Complete task", lambda: tm.complete_task("Lab Report Final"))
    test("Cancel task", lambda: tm.cancel_task("Buy groceries"))
    test("Reopen task", lambda: tm.reopen_task("Lab Report Final"))
    test("Invalid completion", lambda: tm.complete_task("Ghost Task"))

    #recurring task tests
    section("Recurring tasks")

    start = datetime.date(2026, 4, 1)
    end   = datetime.date(2026, 4, 30)

    def daily(): return tm.create_recurring_task("Daily Standup", priority=1, pattern="daily",
                                                start_date=start, end_date=end)
    def weekly(): return tm.create_recurring_task("Gym", priority=2, pattern="weekly",
                                                 weekdays=[0, 2, 4], start_date=start, end_date=end)
    def monthly(): return tm.create_recurring_task("Rent", priority=1, pattern="monthly",
                                                  day_of_month=1, start_date=start, end_date=end)
    def custom(): return tm.create_recurring_task("Water Plants", priority=1, pattern="custom",
                                                 interval_days=3, start_date=start, end_date=end)
    test("Daily recurring", daily)
    test("Weekly recurring", weekly)
    test("Monthly recurring", monthly)
    test("Custom recurring", custom)

    daily_task = tm.get_task("Daily Standup")

    test("Occurrences exist", lambda: len(daily_task.occurrences))
    test("Complete one occurrence", lambda: daily_task.occurrences[0].complete())
    test("Next still open", lambda: daily_task.occurrences[1].is_open())

    #searching
    section("Search")

    test("All open tasks", lambda: [t.title for t in tm.search_tasks()])
    test("Keyword search", lambda: [t.title for t in tm.search_tasks(keyword="midterm")])
    test("Completed tasks", lambda: [t.title for t in tm.search_tasks(status="Completed")])
    test("By tag", lambda: [t.title for t in tm.search_tasks(tag="school")])
    test("By project", lambda: [t.title for t in tm.search_tasks(project_name="Course Assignments")])
    test("Date range",
         lambda: [t.title for t in tm.search_tasks(
             due_after=today,
             due_before=today + datetime.timedelta(days=14)
         )])
    test("Sort by priority", lambda: [t.title for t in tm.view_all_tasks(sort_by="priority")])

    #history
    section("History")

    test("History exists", lambda: len(tm.history.get_history()))
    print("\nLast 5 entries:")
    for ts, name, action in tm.history.get_history()[-5:]:
        print(f"[{ts.strftime('%H:%M:%S')}] {name} -> {action}")
    lab_task = tm.get_task("Lab Report Final")
    test("Task history", lambda: len(lab_task.history))

    #exporting to csv
    section("CSV export")

    csv_output = tm.export_to_csv()
    test("Export all", lambda: len(csv_output.splitlines()))

    #importing from csv
    section("CSV import")

    testcsv = """TaskName,Description,Subtask,Status,Priority,DueDate,ProjectName,ProjectDescription,Collaborator,CollaboratorCategory
Imported Task A,Do something important,,Open,2,2026-05-01,Imported Project,A new project,,
"""

    fresh_tm = TaskManager()

    def import_csv(): return fresh_tm.import_from_csv(testcsv)
    def get_imported(): return fresh_tm.get_project_by_name("Imported Project")

    test("Import CSV", import_csv)
    test("Project created", get_imported)
    print("\nDone.")