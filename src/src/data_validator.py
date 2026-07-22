REQUIRED_COLUMNS = {
    "Source",
    "Relationship",
    "Target",
    "Evidence",
}


def validate_columns(fieldnames):
    if fieldnames is None:
        raise ValueError("The dataset does not contain a header row.")

    missing_columns = REQUIRED_COLUMNS.difference(fieldnames)

    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))

        raise ValueError(
            f"Missing required columns: {missing_text}"
        )


def validate_row(row, row_number):
    empty_fields = []

    for column in REQUIRED_COLUMNS:
        value = row.get(column, "").strip()

        if not value:
            empty_fields.append(column)

    if empty_fields:
        empty_text = ", ".join(sorted(empty_fields))

        raise ValueError(
            f"Row {row_number} contains empty fields: "
            f"{empty_text}"
        )


def validate_dataset(reader):
    validate_columns(reader.fieldnames)

    validated_rows = []

    for row_number, row in enumerate(reader, start=2):
        validate_row(row, row_number)
        validated_rows.append(row)

    if not validated_rows:
        raise ValueError(
            "The biomedical relationships dataset is empty."
        )

    return validated_rows
