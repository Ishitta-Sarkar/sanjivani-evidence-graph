from collections import Counter
from typing import Any


def count_entity_types(
    graph,
    entity_types,
) -> dict[str, int]:
    """Count the biomedical entities belonging to each type."""

    type_counts: Counter[str] = Counter()

    for entity in graph.get_entities():
        entity_type = entity_types.get(
            entity,
            "Unknown",
        )

        type_counts[str(entity_type)] += 1

    return dict(
        sorted(
            type_counts.items(),
            key=lambda item: item[0].lower(),
        )
    )


def get_top_connected_entities(
    graph,
    limit: int = 5,
) -> list[tuple[str, int]]:
    """Return the entities with the highest number of connections."""

    if limit <= 0:
        return []

    ranked_entities = []

    for entity, connections in graph.adjacency.items():
        ranked_entities.append(
            (
                str(entity),
                len(connections),
            )
        )

    ranked_entities.sort(
        key=lambda item: (
            -item[1],
            item[0].lower(),
        )
    )

    return ranked_entities[:limit]


def get_top_entities_by_type(
    graph,
    entity_types,
    requested_type: str,
    limit: int = 5,
) -> list[tuple[str, int]]:
    """Return the most connected entities of one biomedical type."""

    if limit <= 0:
        return []

    matching_entities = []

    for entity, connections in graph.adjacency.items():
        entity_type = entity_types.get(
            entity,
            "Unknown",
        )

        if entity_type.casefold() == requested_type.casefold():
            matching_entities.append(
                (
                    entity,
                    len(connections),
                )
            )

    matching_entities.sort(
        key=lambda item: (
            -item[1],
            item[0].lower(),
        )
    )

    return matching_entities[:limit]


def calculate_graph_density(graph) -> float:
    """Calculate density for the undirected biomedical graph."""

    total_entities = len(graph.adjacency)
    total_relationships = len(graph.relationships)

    if total_entities < 2:
        return 0.0

    maximum_relationships = (
        total_entities * (total_entities - 1)
    ) / 2

    density = total_relationships / maximum_relationships

    return round(
        density,
        4,
    )


def calculate_average_degree(graph) -> float:
    """Calculate the average number of connections per entity."""

    total_entities = len(graph.adjacency)

    if total_entities == 0:
        return 0.0

    total_degree = sum(
        len(connections)
        for connections in graph.adjacency.values()
    )

    return round(
        total_degree / total_entities,
        2,
    )


def calculate_graph_statistics(
    graph,
    entity_types,
) -> dict[str, Any]:
    """Calculate a statistical summary of SANJIVANI."""

    return {
        "total_entities": len(graph.adjacency),
        "total_relationships": len(graph.relationships),
        "entity_types": count_entity_types(
            graph,
            entity_types,
        ),
        "average_degree": calculate_average_degree(graph),
        "graph_density": calculate_graph_density(graph),
        "top_connected_entities": get_top_connected_entities(
            graph,
            limit=5,
        ),
    }


def display_graph_analytics(
    graph,
    entity_types,
) -> None:
    """Display a readable graph analytics report."""

    statistics = calculate_graph_statistics(
        graph,
        entity_types,
    )

    print("\nSANJIVANI Graph Analytics")
    print("=" * 40)

    print(
        f"Total biomedical entities: "
        f"{statistics['total_entities']}"
    )

    print(
        f"Total relationships: "
        f"{statistics['total_relationships']}"
    )

    print(
        f"Average entity degree: "
        f"{statistics['average_degree']}"
    )

    print(
        f"Graph density: "
        f"{statistics['graph_density']}"
    )

    print("\nEntities by type")
    print("-" * 40)

    entity_type_counts = statistics["entity_types"]

    if entity_type_counts:
        for entity_type, count in entity_type_counts.items():
            print(
                f"{entity_type}: {count}"
            )
    else:
        print("No typed entities are available.")

    print("\nMost connected entities")
    print("-" * 40)

    top_entities = statistics[
        "top_connected_entities"
    ]

    if top_entities:
        for rank, (
            entity,
            connection_count,
        ) in enumerate(
            top_entities,
            start=1,
        ):
            print(
                f"{rank}. {entity} — "
                f"{connection_count} connections"
            )
    else:
        print("No connected entities are available.")

    print("=" * 40)