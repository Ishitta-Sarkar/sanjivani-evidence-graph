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
        """Add a biomedical relationship to the graph."""

        relationship_data = {
            "source": source,
            "relationship": relation,
            "target": target,
            "evidence": evidence,
        }

        self.relationships.append(relationship_data)

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
        """Display all relationships in the graph."""

        print("\nBiomedical Knowledge Graph\n")

        for relationship in self.relationships:
            print(
                f"{relationship['source']} "
                f"--{relationship['relationship']}--> "
                f"{relationship['target']} "
                f"[Evidence: {relationship['evidence']}]"
            )

    def find_connections(self, entity_name):
        """Return direct connections while ignoring letter case."""

        actual_entity = self._find_exact_entity(entity_name)

        if actual_entity is None:
            return []

        connections = []

        for connection in self.adjacency.get(actual_entity, []):
            neighbour = connection["neighbour"]
            relationship = connection["relationship"]
            direction = connection["direction"]
            evidence = connection["evidence"]

            connections.append(
                {
                    "entity": neighbour,
                    "connected_to": neighbour,
                    "neighbour": neighbour,
                    "relationship": relationship,
                    "direction": direction,
                    "evidence": evidence,
                    "evidence_source": evidence,
                }
            )

        return connections

    def find_path(self, start_entity, end_entity):
        """Find the shortest path between two biomedical entities."""

        actual_start = self._find_exact_entity(start_entity)
        actual_end = self._find_exact_entity(end_entity)

        if actual_start is None or actual_end is None:
            return []

        if actual_start == actual_end:
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
                        "relationship": connection["relationship"],
                        "target": neighbour,
                        "direction": connection["direction"],
                        "evidence": connection["evidence"],
                        "evidence_source": connection["evidence"],
                    }

                    queue.append(
                        (
                            neighbour,
                            path_steps + [step],
                        )
                    )

        return []

    def get_entities(self):
        """Return all entities alphabetically."""

        return sorted(
            self.adjacency.keys(),
            key=str.lower,
        )

    def get_statistics(self):
        """Return graph statistics."""

        return {
            "total_entities": len(self.adjacency),
            "total_relationships": len(self.relationships),
        }

    def _find_exact_entity(self, entity_name):
        """Find the correctly capitalized entity name."""

        cleaned_name = entity_name.strip().casefold()

        for stored_entity in self.adjacency:
            if stored_entity.casefold() == cleaned_name:
                return stored_entity

        return None