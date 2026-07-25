import os

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D


ENTITY_COLORS = {
    "Disease": "#F28E8E",
    "Gene": "#8EC5FC",
    "Protein": "#B8A1E3",
    "Protein Complex": "#9FD8CB",
    "Pathway": "#F6D58A",
    "Drug": "#A8E6A3",
    "Unknown": "#D3D3D3",
}


def create_graph_visualization(graph, entity_types):
    """
    Create and save a color-coded biomedical graph visualization.
    """

    network = nx.DiGraph()

    for relationship in graph.relationships:
        network.add_edge(
            relationship["source"],
            relationship["target"],
            label=relationship["relationship"],
        )

    plt.figure(figsize=(16, 10))

    positions = nx.spring_layout(
        network,
        seed=42,
        k=1.8,
        iterations=200,
    )

    node_colors = []

    for node in network.nodes:
        entity_type = entity_types.get(node, "Unknown")
        node_colors.append(
            ENTITY_COLORS.get(
                entity_type,
                ENTITY_COLORS["Unknown"],
            )
        )

    nx.draw_networkx_nodes(
        network,
        positions,
        node_size=3200,
        node_color=node_colors,
        edgecolors="black",
        linewidths=1.2,
    )

    nx.draw_networkx_labels(
        network,
        positions,
        font_size=10,
        font_weight="bold",
    )

    nx.draw_networkx_edges(
        network,
        positions,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=20,
        width=1.4,
        connectionstyle="arc3,rad=0.08",
    )

    edge_labels = nx.get_edge_attributes(
        network,
        "label",
    )

    nx.draw_networkx_edge_labels(
        network,
        positions,
        edge_labels=edge_labels,
        font_size=8,
        rotate=False,
        label_pos=0.5,
    )

    legend_items = []

    used_types = sorted(
        {
            entity_types.get(node, "Unknown")
            for node in network.nodes
        }
    )

    for entity_type in used_types:
        legend_items.append(
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                label=entity_type,
                markerfacecolor=ENTITY_COLORS.get(
                    entity_type,
                    ENTITY_COLORS["Unknown"],
                ),
                markeredgecolor="black",
                markersize=12,
            )
        )

    plt.legend(
        handles=legend_items,
        title="Entity Types",
        loc="best",
    )

    plt.title(
        "SANJIVANI Evidence Graph\n"
        "Explainable Biomedical Knowledge Graph",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )

    plt.axis("off")
    plt.tight_layout()

    os.makedirs(
        "visualizations",
        exist_ok=True,
    )

    output_file = (
        "visualizations/"
        "biomedical_graph.png"
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(
        f"\nGraph saved successfully to:\n{output_file}"
    )