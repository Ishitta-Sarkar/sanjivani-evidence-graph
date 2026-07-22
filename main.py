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


def main():
    print("=" * 60)
    print("SANJIVANI Evidence Graph")
    print("=" * 60)

    graph = load_relationships("data/relationships.csv")

    print("\nBiomedical relationships loaded successfully.")

    search_entity = input(
        "\nEnter a disease, gene, protein, pathway, or drug: "
    ).strip()

    connections = graph.find_connections(search_entity)

    display_connections(connections)


if __name__ == "__main__":
    main()
