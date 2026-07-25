from collections import deque


class BiomedicalGraph:
    """Store and analyse biomedical entities and relationships."""

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

        source = str(source).strip()
        relation = str(relation).strip()
        target = str(target).strip()
        evidence = str(evidence).strip()

        if not source:
            raise ValueError("Relationship source cannot be empty.")

        if not relation:
            raise ValueError("Relationship type cannot be empty.")

        if not target:
            raise ValueError("Relationship target cannot be empty.")

        if not evidence:
            evidence = "Not specified"

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
        """Return direct connections while ignoring capitalization."""

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

    def find_path(
        self,
        start_entity,
        end_entity,
        maximum_path_length=None,
    ):
        """
        Find the shortest path between two biomedical entities.

        The graph is explored in both directions so that mechanistic
        connections can be discovered even when relationship arrows differ.
        """

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

            if (
                maximum_path_length is not None
                and len(path_steps) >= maximum_path_length
            ):
                continue

            for connection in self.adjacency.get(
                current_entity,
                [],
            ):
                neighbour = connection["neighbour"]

                if neighbour in visited:
                    continue

                visited.add(neighbour)

                step = {
                    "source": current_entity,
                    "relationship": connection["relationship"],
                    "target": neighbour,
                    "direction": connection["direction"],
                    "evidence": connection["evidence"],
                    "evidence_source": connection["evidence"],
                }

                new_path = path_steps + [step]

                if neighbour == actual_end:
                    return new_path

                queue.append(
                    (
                        neighbour,
                        new_path,
                    )
                )

        return []

    def get_entities(self):
        """Return all graph entities alphabetically."""

        return sorted(
            self.adjacency.keys(),
            key=str.casefold,
        )

    def get_statistics(self):
        """Return basic graph statistics."""

        return {
            "total_entities": len(self.adjacency),
            "total_relationships": len(self.relationships),
        }

    def _find_exact_entity(self, entity_name):
        """Find the stored entity name without requiring exact case."""

        if entity_name is None:
            return None

        cleaned_name = str(entity_name).strip().casefold()

        if not cleaned_name:
            return None

        for stored_entity in self.adjacency:
            if stored_entity.casefold() == cleaned_name:
                return stored_entity

        return None