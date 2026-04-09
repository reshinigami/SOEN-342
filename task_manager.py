class TaskManager:
    def __init__(self):
        self.projects = []

    def add_project(self, project):
        self.projects.append(project)
        print(f'Added project: {project.name}')
    
    def get_projects(self):
        return self.projects
    
    def get_project_by_name(self, name):
        for project in self.projects:
            if project.name == name:
                return project
        return None
    
    def search_tasks(self, keyword):
        results = []
        for project in self.projects:
            results.extend(project.search_tasks(keyword))
        return results
    
    def project_to_csv(self, project_name):
        project = self.get_project_by_name(project_name)
        if project:
            return project.to_csv()
        else:
            print(f'Project "{project_name}" not found.')
            return None
    def project_from_csv(self, project_name, csv_data):
        project = self.get_project_by_name(project_name)
        if project:
            project.from_csv(csv_data)
        else:
            print(f'Project "{project_name}" not found.')