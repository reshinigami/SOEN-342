from entry import Entry


class Project(Entry):
    def __init__(self, name, description=''):
        super().__init__()
        self.name = name
        self.description = description
        self.collaborators = []

    def add_collaborator(self, collaborator):
        if not isinstance(collaborator, Collaborator):
            raise TypeError("Only Collaborator objects can be added to a project.")
        if collaborator not in self.collaborators:
            self.collaborators.append(collaborator)
            self.log(f'Added collaborator: {collaborator.name}')

    def remove_collaborator(self, collaborator):
        if collaborator in self.collaborators:
            self.collaborators.remove(collaborator)
            self.log(f'Removed collaborator: {collaborator.name}')
        else:
            raise ValueError(f'Collaborator "{collaborator.name}" not found in project "{self.name}".')

    def get_collaborator_by_name(self, name):
        for c in self.collaborators:
            if c.name == name:
                return c
        return None

    def __repr__(self):
        return f"<Project '{self.name}'>"


class Collaborator(Entry):
    limt = None 

    def __init__(self, name):
        super().__init__()
        self.name = name

    def category(self):
        raise NotImplementedError("Subclasses must implement category()")

    def get_limit(self):
        if not isinstance(self.limit, int) or self.limit <= 0:
            raise ValueError(f"Collaborator limit must be a positive integer, got: {self.limit}")
        return self.limit

    def __repr__(self):
        return f"<{self.category()} Collaborator '{self.name}'>"


class Junior_Collaborator(Collaborator):
    limit = 10

    def __init__(self, name):
        super().__init__(name)

    def category(self):
        return "Junior"


class Intermediate_Collaborator(Collaborator):
    limit = 5

    def __init__(self, name):
        super().__init__(name)

    def category(self):
        return "Intermediate"


class Senior_Collaborator(Collaborator):
    limit = 2

    def __init__(self, name):
        super().__init__(name)

    def category(self):
        return "Senior"