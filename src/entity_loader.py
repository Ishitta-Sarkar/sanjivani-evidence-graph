import csv
from pathlib import Path


def load_entity_types(file_path):
    """
    Load biomedical entity names and their types from a CSV file.

    Parameters
    ----------
    file_path : str or Path
        Path to the entities CSV file.

    Returns
    -------
    dict
        Dictionary mapping each entity name to its biomedical type.
    """

    file_path = Path(file_path)
    entity_types = {}

    if not file_path.exists():
        raise FileNotFoundError(
            f"Entity dataset was not found: {file_path}"
        )

    with file_path.open(
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        required_columns = {"Entity", "Type"}

        if reader.fieldnames is None:
            raise ValueError("The entity dataset is empty.")

        missing_columns = required_columns - set(reader.fieldnames)

        if missing_columns:
            raise ValueError(
                "Missing required columns: "
                + ", ".join(sorted(missing_columns))
            )

        for row_number, row in enumerate(reader, start=2):
            entity = row["Entity"].strip()
            entity_type = row["Type"].strip()

            if not entity:
                raise ValueError(
                    f"Missing entity name on row {row_number}."
                )

            if not entity_type:
                raise ValueError(
                    f"Missing entity type on row {row_number}."
                )

            entity_types[entity] = entity_type

    return entity_types
    if __name__ == "__main__":
    entity_types = load_entity_types("data/entities.csv")

    print("Loaded entity types:\n")

    for entity, entity_type in entity_types.items():
        print(f"{entity} -> {entity_type}")
