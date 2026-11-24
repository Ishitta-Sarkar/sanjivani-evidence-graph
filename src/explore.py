"""Undirected path search and drug-repurposing candidates for the web app.

The command-line explorer uses ``BiomedicalGraph`` in ``graph_builder.py``.
These functions are the ones the Streamlit pages call. Both treat a
relationship as traversable in either direction.
"""

from collections import deque

import networkx as nx
import pandas as pd

from src.entities import format_relationship_name



def build_graph_adjacency(
    relationships: pd.DataFrame,
) -> dict[str, list[str]]:
    """Build an undirected adjacency list."""

    adjacency: dict[str, list[str]] = {}

    for _, row in relationships.iterrows():
        source = str(row["Source"])
        target = str(row["Target"])

        adjacency.setdefault(
            source,
            [],
        )

        adjacency.setdefault(
            target,
            [],
        )

        if target not in adjacency[source]:
            adjacency[source].append(
                target
            )

        if source not in adjacency[target]:
            adjacency[target].append(
                source
            )

    return adjacency

def find_shortest_path(
    start_entity: str,
    end_entity: str,
    adjacency: dict[str, list[str]],
    max_edges: int = 4,
) -> list[str] | None:
    """Find a shortest graph path using BFS."""

    if start_entity == end_entity:
        return [start_entity]

    if start_entity not in adjacency:
        return None

    if end_entity not in adjacency:
        return None

    queue = deque(
        [
            (
                start_entity,
                [start_entity],
            )
        ]
    )

    visited = {start_entity}

    while queue:
        current_entity, current_path = (
            queue.popleft()
        )

        edges_used = len(current_path) - 1

        if edges_used >= max_edges:
            continue

        for neighbour in adjacency.get(
            current_entity,
            [],
        ):
            if neighbour in visited:
                continue

            new_path = (
                current_path
                + [neighbour]
            )

            if neighbour == end_entity:
                return new_path

            visited.add(neighbour)

            queue.append(
                (
                    neighbour,
                    new_path,
                )
            )

    return None

def get_relationship_between(
    first_entity: str,
    second_entity: str,
    relationships: pd.DataFrame,
) -> dict[str, str] | None:
    """Return relationship details between two entities."""

    direct_match = relationships[
        (
            relationships["Source"]
            .str.casefold()
            == first_entity.casefold()
        )
        &
        (
            relationships["Target"]
            .str.casefold()
            == second_entity.casefold()
        )
    ]

    if not direct_match.empty:
        row = direct_match.iloc[0]

        return {
            "Source": str(row["Source"]),
            "Relationship": str(
                row["Relationship"]
            ),
            "Target": str(row["Target"]),
            "Evidence": str(
                row["Evidence"]
            ),
            "Traversal": "forward",
        }

    reverse_match = relationships[
        (
            relationships["Source"]
            .str.casefold()
            == second_entity.casefold()
        )
        &
        (
            relationships["Target"]
            .str.casefold()
            == first_entity.casefold()
        )
    ]

    if not reverse_match.empty:
        row = reverse_match.iloc[0]

        return {
            "Source": str(row["Source"]),
            "Relationship": str(
                row["Relationship"]
            ),
            "Target": str(row["Target"]),
            "Evidence": str(
                row["Evidence"]
            ),
            "Traversal": "reverse",
        }

    return None

def describe_path(
    path: list[str],
    relationships: pd.DataFrame,
) -> list[dict[str, str]]:
    """Convert a graph path into explainable steps."""

    steps: list[dict[str, str]] = []

    for index in range(
        len(path) - 1
    ):
        current_entity = path[index]
        next_entity = path[index + 1]

        relationship_data = (
            get_relationship_between(
                current_entity,
                next_entity,
                relationships,
            )
        )

        if relationship_data is None:
            continue

        if (
            relationship_data["Traversal"]
            == "forward"
        ):
            arrow = "→"
        else:
            arrow = "←"

        steps.append(
            {
                "From": current_entity,
                "Arrow": arrow,
                "Relationship": (
                    relationship_data[
                        "Relationship"
                    ]
                ),
                "To": next_entity,
                "Evidence": (
                    relationship_data[
                        "Evidence"
                    ]
                ),
            }
        )

    return steps

def create_path_summary(
    path: list[str],
    relationships: pd.DataFrame,
) -> str:
    """Create a readable path summary."""

    if len(path) == 1:
        return path[0]

    parts = [path[0]]

    for index in range(
        len(path) - 1
    ):
        current_entity = path[index]
        next_entity = path[index + 1]

        relationship_data = (
            get_relationship_between(
                current_entity,
                next_entity,
                relationships,
            )
        )

        if relationship_data is None:
            parts.append(
                "— Connected To →"
            )

            parts.append(
                next_entity
            )

            continue

        relationship_name = (
            format_relationship_name(
                relationship_data[
                    "Relationship"
                ]
            )
        )

        if (
            relationship_data["Traversal"]
            == "forward"
        ):
            parts.append(
                f"— {relationship_name} →"
            )
        else:
            parts.append(
                f"← {relationship_name} —"
            )

        parts.append(
            next_entity
        )

    return " ".join(parts)

def collect_path_evidence(
    path: list[str],
    relationships: pd.DataFrame,
) -> list[str]:
    """Collect unique evidence sources."""

    evidence_sources: list[str] = []

    path_steps = describe_path(
        path,
        relationships,
    )

    for step in path_steps:
        evidence = step["Evidence"]

        if (
            evidence
            and evidence.casefold()
            != "nan"
            and evidence
            not in evidence_sources
        ):
            evidence_sources.append(
                evidence
            )

    return evidence_sources

def get_drug_recommendations(
    selected_disease: str,
    entities: pd.DataFrame,
    relationships: pd.DataFrame,
    max_edges: int = 4,
) -> list[dict[str, object]]:
    """Generate graph-derived drug recommendations."""

    adjacency = build_graph_adjacency(
        relationships
    )

    drug_names = (
        entities[
            entities["Type"]
            .str.casefold()
            == "drug"
        ]["Entity"]
        .drop_duplicates()
        .tolist()
    )

    recommendations: list[
        dict[str, object]
    ] = []

    for drug_name in drug_names:
        path = find_shortest_path(
            start_entity=drug_name,
            end_entity=selected_disease,
            adjacency=adjacency,
            max_edges=max_edges,
        )

        if path is None:
            continue

        path_steps = describe_path(
            path,
            relationships,
        )

        if not path_steps:
            continue

        is_direct_treatment = (
            len(path) == 2
            and path_steps[0][
                "Relationship"
            ].casefold()
            == "treats"
            and path_steps[0][
                "Arrow"
            ]
            == "→"
        )

        if is_direct_treatment:
            recommendation_type = (
                "Direct treatment relationship"
            )

            confidence_label = (
                "Direct graph evidence"
            )

            rank = 0

        else:
            recommendation_type = (
                "Mechanism-linked graph candidate"
            )

            confidence_label = (
                "Graph-derived mechanistic connection"
            )

            rank = len(path) - 1

        recommendations.append(
            {
                "Drug": drug_name,
                "Path": path,
                "Steps": path_steps,
                "Path Length": (
                    len(path) - 1
                ),
                "Recommendation Type": (
                    recommendation_type
                ),
                "Confidence Label": (
                    confidence_label
                ),
                "Evidence Sources": (
                    collect_path_evidence(
                        path,
                        relationships,
                    )
                ),
                "Rank": rank,
            }
        )

    recommendations.sort(
        key=lambda item: (
            int(item["Rank"]),
            str(item["Drug"]),
        )
    )

    return recommendations

def get_nodes_within_depth(
    selected_entity: str,
    relationships: pd.DataFrame,
    depth: int,
) -> set[str]:
    """Return nearby nodes for focused graph mode."""

    adjacency = build_graph_adjacency(
        relationships
    )

    visited = {selected_entity}
    current_level = {selected_entity}

    for _ in range(depth):
        next_level: set[str] = set()

        for entity in current_level:
            next_level.update(
                adjacency.get(
                    entity,
                    [],
                )
            )

        next_level.difference_update(
            visited
        )

        if not next_level:
            break

        visited.update(
            next_level
        )

        current_level = next_level

    return visited

def find_shortest_entity_path(
    start_entity: str,
    end_entity: str,
    relationships: pd.DataFrame,
) -> list[str] | None:
    """
    Find the shortest connection between two biomedical entities.

    The graph is treated as undirected during path searching so that
    connections can be explored even when an edge points in the
    opposite biological direction.
    """

    if not start_entity or not end_entity:
        return None

    if start_entity == end_entity:
        return [start_entity]

    graph = nx.Graph()

    for _, relationship in relationships.iterrows():
        source = str(relationship["Source"]).strip()
        target = str(relationship["Target"]).strip()

        if source and target:
            graph.add_edge(source, target)

    if start_entity not in graph:
        return None

    if end_entity not in graph:
        return None

    try:
        return nx.shortest_path(
            graph,
            source=start_entity,
            target=end_entity,
        )

    except nx.NetworkXNoPath:
        return None

    except nx.NodeNotFound:
        return None
