"""Entity labels, colours, and icons shared by the interface."""

import pandas as pd



def get_entity_type(
    entity_name: str,
    entities: pd.DataFrame,
) -> str:
    """Return the type of an entity."""

    matching_entity = entities[
        entities["Entity"].str.casefold()
        == entity_name.casefold()
    ]

    if matching_entity.empty:
        return "Unknown"

    return str(
        matching_entity.iloc[0]["Type"]
    )

def get_entity_icon(
    entity_type: str,
) -> str:
    """Return an icon for an entity type."""

    icon_map = {
        "Disease": "🦠",
        "Gene": "🧬",
        "Protein": "🔬",
        "Protein Complex": "🧩",
        "Pathway": "🔗",
        "Drug": "💊",
    }

    return icon_map.get(
        entity_type,
        "◉",
    )

def get_node_color(
    entity_type: str,
) -> str:
    """Return a colour for an entity type."""

    colour_map = {
        "Disease": "#ef4444",
        "Gene": "#8b5cf6",
        "Protein": "#3b82f6",
        "Protein Complex": "#06b6d4",
        "Pathway": "#f59e0b",
        "Drug": "#10b981",
        "Unknown": "#94a3b8",
    }

    return colour_map.get(
        entity_type,
        "#94a3b8",
    )

def format_relationship_name(
    relationship: str,
) -> str:
    """Make relationship names readable."""

    return relationship.replace(
        "_",
        " ",
    ).title()
