import csv

print("=" * 60)
print("SANJIVANI Evidence Graph")
print("=" * 60)

print("\nLoading biomedical relationships...\n")

with open("data/relationships.csv", "r") as file:
    reader = csv.DictReader(file)

    for row in reader:
        print(
            f"{row['Source']} --{row['Relationship']}--> {row['Target']}"
        )

print("\nDataset loaded successfully.")
