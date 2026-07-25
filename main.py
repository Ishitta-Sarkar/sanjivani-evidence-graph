import csv

from src.data_validator import validate_dataset
from src.entity_loader import load_entity_types
from src.graph_builder import BiomedicalGraph
from src.entity_loader import load_entity_types

RELATIONSHIPS_FILE = "data/relationships.csv"
ENTITIES_FILE = "data/entities.csv"


def load_relationships(file_path):
    """Load validated biomedical relationships into the graph."""

    graph = BiomedicalGraph()

    with open(file_path, "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        validated_rows = validate_dataset(reader)

        for row in validated_rows:
            graph.add_relationship(
                row["Source"],
                row["Relationship"],
                row["Target"],
                row["Evidence"],
            )

    return graph


def find_entity_type(entity_name, entity_types):
    """Find an entity type without requiring exact capitalization."""

    cleaned_name = entity_name.strip().casefold()

    for entity, entity_type in entity_types.items():
        if entity.casefold() == cleaned_name:
            return entity_type

    return "Unknown"


def display_connections(search_entity, connections, entity_types):
    """Display direct biomedical connections and evidence."""

    entity_type = find_entity_type(search_entity, entity_types)

    print("\nEntity Information")
    print("-" * 30)
    print(f"Entity: {search_entity}")
    print(f"Type: {entity_type}")

    if not connections:
        print("\nNo connections were found for this entity.")
        return

    print("\nConnections found:\n")

    for connection in connections:
        connected_entity = connection["connected_to"]
        connected_type = find_entity_type(
            connected_entity,
            entity_types,
        )

        if connection["direction"] == "forward":
            print(
                f"{connection['entity']} "
                f"--{connection['relationship']}--> "
                f"{connected_entity} [{connected_type}]"
            )
        else:
            print(
                f"{connection['entity']} "
                f"<--{connection['relationship']}-- "
                f"{connected_entity} [{connected_type}]"
            )

        print(f"Evidence source: {connection['evidence']}\n")


def display_path(path, entity_types):
    """Display an explainable biomedical path."""

    if not path:
        print("\nNo connecting path was found.")
        return

    print("\nExplainable biomedical path:\n")

    for step in path:
        source_type = find_entity_type(
            step["source"],
            entity_types,
        )
        target_type = find_entity_type(
            step["target"],
            entity_types,
        )

        if step["direction"] == "forward":
            print(
                f"{step['source']} [{source_type}] "
                f"--{step['relationship']}--> "
                f"{step['target']} [{target_type}]"
            )
        else:
            print(
                f"{step['source']} [{source_type}] "
                f"<--{step['relationship']}-- "
                f"{step['target']} [{target_type}]"
            )

        print(f"Evidence source: {step['evidence']}\n")


def display_entities(entities, entity_types):
    """Display all available entities with their biomedical types."""

    print("\nAvailable biomedical entities:\n")

    for number, entity in enumerate(entities, start=1):
        entity_type = find_entity_type(entity, entity_types)
        print(f"{number}. {entity} [{entity_type}]")


def main():
    """Run the SANJIVANI interactive application."""

    print("=" * 60)
    print("SANJIVANI Evidence Graph")
    print("=" * 60)

    try:
        graph = load_relationships(RELATIONSHIPS_FILE)
        entity_types = load_entity_types(ENTITIES_FILE)

    except FileNotFoundError as error:
        print(f"\nFile error: {error}")
        return

    except ValueError as error:
        print(f"\nDataset validation error: {error}")
        return

    print("\nDatasets validated and loaded successfully.")

    statistics = graph.get_statistics()

    print("\nGraph Summary")
    print("-" * 30)
    print(
        f"Total biomedical entities: "
        f"{statistics['total_entities']}"
    )
    print(
        f"Total relationships: "
        f"{statistics['total_relationships']}"
    )
    print(
        f"Typed entities available: "
        f"{len(entity_types)}"
    )

    while True:
        print("\nMenu")
        print("-" * 30)
        print("1. Search for direct connections")
        print("2. Find a path between two entities")
        print("3. Show all available entities")
        print("4. Exit")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            search_entity = input(
                "\nEnter a disease, gene, protein, pathway, or drug: "
            ).strip()

            connections = graph.find_connections(search_entity)

            display_connections(
                search_entity,
                connections,
                entity_types,
            )

        elif choice == "2":
            start_entity = input(
                "\nEnter the starting entity: "
            ).strip()

            end_entity = input(
                "Enter the ending entity: "
            ).strip()

            path = graph.find_path(
                start_entity,
                end_entity,
            )

            display_path(path, entity_types)

        elif choice == "3":
            entities = graph.get_entities()
            display_entities(entities, entity_types)

        elif choice == "4":
            print("\nExiting SANJIVANI. Goodbye!")
            break

        else:
            print("\nInvalid option. Please select 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()