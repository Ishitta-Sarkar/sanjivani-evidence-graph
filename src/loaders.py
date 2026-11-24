"""Load the curated SANJIVANI tables used by the web application."""

from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ENTITIES_FILE = PROJECT_ROOT / "data" / "entities.csv"
RELATIONSHIPS_FILE = PROJECT_ROOT / "data" / "relationships.csv"

VISUALIZATIONS_FOLDER = PROJECT_ROOT / "visualizations"

GRAPH_IMAGE_CANDIDATES = [
    VISUALIZATIONS_FOLDER / "biomedical_graph.png",
    VISUALIZATIONS_FOLDER / "knowledge_graph.png",
    VISUALIZATIONS_FOLDER / "graph_visualization.png",
]



@st.cache_data
def load_entities() -> pd.DataFrame:
    """Load and clean entities.csv."""

    entities = pd.read_csv(ENTITIES_FILE)

    entities = entities.dropna(how="all")
    entities.columns = entities.columns.str.strip()

    required_columns = {"Entity", "Type"}

    missing_columns = required_columns.difference(
        entities.columns
    )

    if missing_columns:
        raise ValueError(
            "entities.csv is missing these columns: "
            + ", ".join(sorted(missing_columns))
        )

    entities["Entity"] = (
        entities["Entity"]
        .astype(str)
        .str.strip()
    )

    entities["Type"] = (
        entities["Type"]
        .astype(str)
        .str.strip()
    )

    entities = entities[
        entities["Entity"].ne("")
        & entities["Type"].ne("")
    ]

    entities = entities.drop_duplicates(
        subset=["Entity"],
        keep="first",
    )

    return entities.reset_index(drop=True)

@st.cache_data
def load_relationships() -> pd.DataFrame:
    """Load and clean relationships.csv."""

    relationships = pd.read_csv(
        RELATIONSHIPS_FILE
    )

    relationships = relationships.dropna(
        how="all"
    )

    relationships.columns = (
        relationships.columns.str.strip()
    )

    required_columns = {
        "Source",
        "Relationship",
        "Target",
        "Evidence",
    }

    missing_columns = required_columns.difference(
        relationships.columns
    )

    if missing_columns:
        raise ValueError(
            "relationships.csv is missing these columns: "
            + ", ".join(sorted(missing_columns))
        )

    for column in required_columns:
        relationships[column] = (
            relationships[column]
            .astype(str)
            .str.strip()
        )

    relationships = relationships[
        relationships["Source"].ne("")
        & relationships["Relationship"].ne("")
        & relationships["Target"].ne("")
    ]

    relationships = relationships.drop_duplicates(
        subset=[
            "Source",
            "Relationship",
            "Target",
            "Evidence",
        ]
    )

    return relationships.reset_index(drop=True)

def get_graph_image() -> Path | None:
    """Find an existing static graph image."""

    for image_path in GRAPH_IMAGE_CANDIDATES:
        if image_path.exists():
            return image_path

    if VISUALIZATIONS_FOLDER.exists():
        png_files = sorted(
            VISUALIZATIONS_FOLDER.glob(
                "*.png"
            )
        )

        if png_files:
            return png_files[0]

    return None
