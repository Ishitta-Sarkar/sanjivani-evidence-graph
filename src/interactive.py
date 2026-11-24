"""PyVis figures for the full graph and for one selected path."""

import pandas as pd
from pyvis.network import Network

from src.entities import (
    format_relationship_name,
    get_entity_icon,
    get_entity_type,
    get_node_color,
)
from src.explore import get_nodes_within_depth, get_relationship_between



def create_interactive_graph_html(
    entities: pd.DataFrame,
    relationships: pd.DataFrame,
    selected_entity: str | None = None,
    depth: int = 2,
) -> tuple[str, int, int]:
    """Create an interactive PyVis graph."""

    graph_relationships = (
        relationships.copy()
    )

    if selected_entity is not None:
        visible_nodes = (
            get_nodes_within_depth(
                selected_entity,
                relationships,
                depth,
            )
        )

        graph_relationships = (
            relationships[
                relationships[
                    "Source"
                ].isin(visible_nodes)
                &
                relationships[
                    "Target"
                ].isin(visible_nodes)
            ].copy()
        )

    graph_nodes = sorted(
        set(
            graph_relationships[
                "Source"
            ]
        )
        |
        set(
            graph_relationships[
                "Target"
            ]
        )
    )

    network = Network(
        height="720px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="#111827",
        cdn_resources="in_line",
    )

    network.set_options(
        """
        {
          "nodes": {
            "borderWidth": 2,
            "font": {
              "size": 16,
              "face": "Arial"
            },
            "shadow": true
          },
          "edges": {
            "arrows": {
              "to": {
                "enabled": true,
                "scaleFactor": 0.7
              }
            },
            "font": {
              "size": 11,
              "align": "middle"
            },
            "smooth": {
              "enabled": true,
              "type": "dynamic"
            }
          },
          "interaction": {
            "hover": true,
            "navigationButtons": true,
            "keyboard": true,
            "tooltipDelay": 100
          },
          "physics": {
            "enabled": true,
            "barnesHut": {
              "gravitationalConstant": -6000,
              "centralGravity": 0.25,
              "springLength": 180,
              "springConstant": 0.04,
              "damping": 0.12
            },
            "stabilization": {
              "enabled": true,
              "iterations": 600
            }
          }
        }
        """
    )

    for node_name in graph_nodes:
        entity_type = get_entity_type(
            node_name,
            entities,
        )

        entity_icon = get_entity_icon(
            entity_type
        )

        node_colour = get_node_color(
            entity_type
        )

        is_selected = (
            selected_entity is not None
            and node_name.casefold()
            == selected_entity.casefold()
        )

        network.add_node(
            node_name,
            label=node_name,
            title=(
                f"{entity_icon} {node_name}"
                f"<br>Entity Type: "
                f"{entity_type}"
            ),
            color={
                "background": (
                    node_colour
                ),
                "border": (
                    "#111827"
                    if is_selected
                    else node_colour
                ),
                "highlight": {
                    "background": (
                        node_colour
                    ),
                    "border": (
                        "#111827"
                    ),
                },
            },
            size=(
                30
                if is_selected
                else 22
            ),
            shape="dot",
        )

    for _, row in (
        graph_relationships.iterrows()
    ):
        relationship_label = (
            format_relationship_name(
                str(
                    row[
                        "Relationship"
                    ]
                )
            )
        )

        evidence = str(
            row["Evidence"]
        )

        network.add_edge(
            str(row["Source"]),
            str(row["Target"]),
            label=relationship_label,
            title=(
                "Relationship: "
                f"{relationship_label}"
                "<br>Evidence: "
                f"{evidence}"
            ),
        )

    graph_html = (
        network.generate_html(
            notebook=False
        )
    )

    return (
        graph_html,
        len(graph_nodes),
        len(graph_relationships),
    )

def create_path_graph_html(
    path: list[str],
    entities: pd.DataFrame,
    relationships: pd.DataFrame,
) -> str:
    """Create an interactive graph for one selected path."""

    network = Network(
        height="620px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="#111827",
        cdn_resources="in_line",
    )

    network.set_options(
        """
        {
          "nodes": {
            "borderWidth": 2,
            "font": {
              "size": 17,
              "face": "Arial"
            },
            "shadow": true
          },
          "edges": {
            "arrows": {
              "to": {
                "enabled": true,
                "scaleFactor": 0.8
              }
            },
            "font": {
              "size": 12,
              "align": "middle"
            },
            "smooth": {
              "enabled": true,
              "type": "dynamic"
            }
          },
          "interaction": {
            "hover": true,
            "navigationButtons": true,
            "keyboard": true
          },
          "physics": {
            "enabled": true,
            "stabilization": {
              "enabled": true,
              "iterations": 400
            }
          }
        }
        """
    )

    for index, node_name in enumerate(path):
        entity_type = get_entity_type(
            node_name,
            entities,
        )

        entity_icon = get_entity_icon(
            entity_type
        )

        node_colour = get_node_color(
            entity_type
        )

        if index == 0:
            node_role = "Start Entity"
            node_size = 32

        elif index == len(path) - 1:
            node_role = "End Entity"
            node_size = 32

        else:
            node_role = "Intermediate Entity"
            node_size = 24

        network.add_node(
            node_name,
            label=node_name,
            title=(
                f"{entity_icon} {node_name}"
                f"<br>Entity Type: {entity_type}"
                f"<br>Path Role: {node_role}"
            ),
            color={
                "background": node_colour,
                "border": "#111827",
                "highlight": {
                    "background": node_colour,
                    "border": "#111827",
                },
            },
            size=node_size,
            shape="dot",
        )

    for index in range(len(path) - 1):
        current_entity = path[index]
        next_entity = path[index + 1]

        relationship_data = get_relationship_between(
            current_entity,
            next_entity,
            relationships,
        )

        if relationship_data is None:
            continue

        relationship_label = format_relationship_name(
            relationship_data["Relationship"]
        )

        evidence = relationship_data["Evidence"]

        if relationship_data["Traversal"] == "forward":
            edge_source = current_entity
            edge_target = next_entity

        else:
            edge_source = next_entity
            edge_target = current_entity

        network.add_edge(
            edge_source,
            edge_target,
            label=relationship_label,
            title=(
                f"Relationship: {relationship_label}"
                f"<br>Evidence: {evidence}"
            ),
            width=3,
        )

    return network.generate_html(
        notebook=False
    )
