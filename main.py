import csv

from src.data_validator import validate_dataset
from src.graph_builder import BiomedicalGraph


def load_relationships(file_path):
    graph = BiomedicalGraph()

    with open(file_path, "r", encoding="utf-8") as file:
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


def display_connections(connections):
    if not connections:
        print("\nNo connections were found for this entity.")
        return

    print("\nConnections found:\n")

    for connection in connections:
        if connection["direction"] == "forward":
            print(
                f"{connection['entity']} "
                f"--{connection['relationship']}--> "
                f"{connection['connected_to']}"
            )
        else:
            print(
                f"{connection['entity']} "
                f"<--{connection['relationship']}-- "
                f"{connection['connected_to']}"
            )

        print(
            f"Evidence source: {connection['evidence']}\n"
        )


def display_path(path):
    if not path:
        print("\nNo connecting path was found.")
        return

    print("\nExplainable biomedical path:\n")

    for step in path:
        if step["direction"] == "forward":
            print(
                f"{step['source']} "
                f"--{step['relationship']}--> "
                f"{step['target']}"
            )
        else:
            print(
                f"{step['source']} "
                f"<--{step['relationship']}-- "
                f"{step['target']}"
            )

        print(
            f"Evidence source: {step['evidence']}\n"
        )


def main():
    print("=" * 60)
    print("SANJIVANI Evidence Graph")
    print("=" * 60)

    try:
        graph = load_relationships(
            "data/relationships.csv"
        )

    except FileNotFoundError:
        print(
            "\nError: The biomedical relationships dataset "
            "could not be found."
        )
        return

    except ValueError as error:
        print(f"\nDataset validation error: {error}")
        return

    print("\nDataset validated and loaded successfully.")

    print("\n1. Search for direct connections")
    print("2. Find a path between two entities")

    choice = input(
        "\nSelect an option: "
    ).strip()

    if choice == "1":
        search_entity = input(
            "\nEnter a disease, gene, protein, pathway, or drug: "
        ).strip()

        connections = graph.find_connections(
            search_entity
        )

        display_connections(connections)

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

        display_path(path)

    else:
        print("\nInvalid option. Please select 1 or 2.")


if __name__ == "__main__":
    main()
