from collections import deque


class BiomedicalGraph:

    def __init__(self):
        self.relationships = []
        self.adjacency = {}

    def add_relationship(self, source, relation, target):
        self.relationships.append(
            (source, relation, target)
        )

        if source not in self.adjacency:
            self.adjacency[source] = []

        if target not in self.adjacency:
            self.adjacency[target] = []

        self.adjacency[source].append(
            (target, relation)
        )

        self.adjacency[target].append(
            (source, relation)
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

    def find_path(self, start_entity, end_entity):
        actual_start = self._find_exact_entity(start_entity)
        actual_end = self._find_exact_entity(end_entity)

        if actual_start is None or actual_end is None:
            return []

        queue = deque(
            [(actual_start, [actual_start])]
        )

        visited = {actual_start}

        while queue:
            current_entity, path = queue.popleft()

            if current_entity == actual_end:
                return path

            for neighbour, _ in self.adjacency.get(
                current_entity,
                [],
            ):
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(
                        (
                            neighbour,
                            path + [neighbour],
                        )
                    )

        return []

    def _find_exact_entity(self, entity):
        for stored_entity in self.adjacency:
            if stored_entity.lower() == entity.lower():
                return stored_entity

        return None
