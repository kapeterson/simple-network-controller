class vlan():

    def __init__(self, id=None, name=None, description=None):
        self.id = id
        self.name = name
        self.description = description

    def toJSON(self):
        return {
            "id" : self.id,
            "name" : self.name,
            "description": self.description
        }

    def __eq__(self, other):

        return self.id == other.id and self.name == other.name
