from collections import deque


class BiomedicalGraph:

    def __init__(self):
        self.relationships = []
        self.adjacency = {}

    def add_relationship(
        self,
        source,
        relation,
        target,
        evidence="Not specified",
    ):
        self.relationships.append(
            {
                "source": source,
                "relationship": relation,
                "target": target,
                "evidence": evidence,
            }
        )

        if source not in self.adjacency:
            self.adjacency[source] = []

        if target not in self.adjacency:
            self.adjacency[target] = []

        self.adjacency[source].append(
            {
                "neighbour": target,
                "relationship": relation,
                "direction": "forward",
                "evidence": evidence,
            }
        )

        self.adjacency[target].append(
            {
                "neighbour": source,
                "relationship": relation,
                "direction": "reverse",
                "evidence": evidence,
            }
        )

    def display(self):
        print("\nBiomedical Knowledge Graph\n")

        for relationship in self.relationships:
            print(
                f"{relationship['source']} "
                f"--{relationship['relationship']}--> "
                f"{relationship['target']} "
                f"[Evidence: {relationship['evidence']}]"
            )

    def find_connections(self, entity):
        connections = []
        actual_entity = self._find_exact_entity(entity)

        if actual_entity is None:
            return connections

        for connection in self.adjacency.get(
            actual_entity,
            [],
        ):
            connections.append(
                {
                    "entity": actual_entity,
                    "relationship": connection["relationship"],
                    "connected_to": connection["neighbour"],
                    "direction": connection["direction"],
                    "evidence": connection["evidence"],
                }
            )

        return connections

    def find_path(self, start_entity, end_entity):
        actual_start = self._find_exact_entity(
            start_entity
        )
        actual_end = self._find_exact_entity(
            end_entity
        )

        if actual_start is None or actual_end is None:
            return []

        queue = deque(
            [
                (
                    actual_start,
                    [],
                )
            ]
        )

        visited = {actual_start}

        while queue:
            current_entity, path_steps = queue.popleft()

            if current_entity == actual_end:
                return path_steps

            for connection in self.adjacency.get(
                current_entity,
                [],
            ):
                neighbour = connection["neighbour"]

                if neighbour not in visited:
                    visited.add(neighbour)

                    step = {
                        "source": current_entity,
                        "relationship": connection[
                            "relationship"
                        ],
                        "target": neighbour,
                        "direction": connection[
                            "direction"
                        ],
                        "evidence": connection[
                            "evidence"
                        ],
                    }

                    queue.append(
                        (
                            neighbour,
                            path_steps + [step],
                        )
                    )

        return []
            def get_entities(self):
        return sorted(
            self.adjacency.keys(),
            key=str.lower,
        )
    def get_statistics(self):
        return {
            "total_entities": len(self.adjacency),
            "total_relationships": len(self.relationships),
        }
    def _find_exact_entity(self, entity):
        for stored_entity in self.adjacency:
            if stored_entity.lower() == entity.lower():
                return stored_entity

        return None
