import csv

from src.graph_builder import BiomedicalGraph


def load_relationships(file_path):
    graph = BiomedicalGraph()

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            graph.add_relationship(
                row["Source"],
                row["Relationship"],
                row["Target"],
            )

    return graph


def display_connections(connections):
    if not connections:
        print("\nNo connections were found for this entity.")
        return

    print("\nConnections found:\n")

    for connection in connections:
        print(
            f"{connection['entity']} "
            f"--{connection['relationship']}--> "
            f"{connection['connected_to']}"
        )


def display_path(path):
    if not path:
        print("\nNo connecting path was found.")
        return

    print("\nConnecting path:\n")
    print(" → ".join(path))


def main():
    print("=" * 60)
    print("SANJIVANI Evidence Graph")
    print("=" * 60)

    graph = load_relationships(
        "data/relationships.csv"
    )

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
