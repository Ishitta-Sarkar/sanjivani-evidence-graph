class BiomedicalGraph:

    def __init__(self):
        self.relationships = []

    def add_relationship(self, source, relation, target):
        self.relationships.append(
            (source, relation, target)
        )

    def display(self):

        print("\nBiomedical Knowledge Graph\n")

        for source, relation, target in self.relationships:
            print(f"{source} --{relation}--> {target}")
