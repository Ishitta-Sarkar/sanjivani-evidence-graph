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


def main():
    print("=" * 60)
    print("SANJIVANI Evidence Graph")
    print("=" * 60)

    graph = load_relationships("data/relationships.csv")

    print("\nBiomedical relationships loaded successfully.")
    graph.display()


if __name__ == "__main__":
    main()
