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

    def find_connections(self, entity):
        connections = []

        for source, relation, target in self.relationships:
            if entity.lower() == source.lower():
                connections.append(
                    {
                        "entity": source,
                        "relationship": relation,
                        "connected_to": target,
                    }
                )

            elif entity.lower() == target.lower():
                connections.append(
                    {
                        "entity": target,
                        "relationship": relation,
                        "connected_to": source,
                    }
                )

        return connections
