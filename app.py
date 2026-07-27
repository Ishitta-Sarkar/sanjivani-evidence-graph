from collections import deque
from pathlib import Path
from datetime import datetime

import pandas as pd
import networkx as nx
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network


# ==================================================
# PAGE SETTINGS
# ==================================================

st.set_page_config(
    page_title="SANJIVANI Evidence Graph",
    page_icon="🧬",
    layout="wide",
)


# ==================================================
# FILE LOCATIONS
# ==================================================

PROJECT_ROOT = Path(__file__).parent

ENTITIES_FILE = PROJECT_ROOT / "data" / "entities.csv"
RELATIONSHIPS_FILE = PROJECT_ROOT / "data" / "relationships.csv"

VISUALIZATIONS_FOLDER = PROJECT_ROOT / "visualizations"

GRAPH_IMAGE_CANDIDATES = [
    VISUALIZATIONS_FOLDER / "biomedical_graph.png",
    VISUALIZATIONS_FOLDER / "knowledge_graph.png",
    VISUALIZATIONS_FOLDER / "graph_visualization.png",
]


# ==================================================
# DATA LOADING
# ==================================================

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


# ==================================================
# ENTITY HELPERS
# ==================================================

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


# ==================================================
# GRAPH HELPERS
# ==================================================

def build_graph_adjacency(
    relationships: pd.DataFrame,
) -> dict[str, list[str]]:
    """Build an undirected adjacency list."""

    adjacency: dict[str, list[str]] = {}

    for _, row in relationships.iterrows():
        source = str(row["Source"])
        target = str(row["Target"])

        adjacency.setdefault(
            source,
            [],
        )

        adjacency.setdefault(
            target,
            [],
        )

        if target not in adjacency[source]:
            adjacency[source].append(
                target
            )

        if source not in adjacency[target]:
            adjacency[target].append(
                source
            )

    return adjacency


def find_shortest_path(
    start_entity: str,
    end_entity: str,
    adjacency: dict[str, list[str]],
    max_edges: int = 4,
) -> list[str] | None:
    """Find a shortest graph path using BFS."""

    if start_entity == end_entity:
        return [start_entity]

    if start_entity not in adjacency:
        return None

    if end_entity not in adjacency:
        return None

    queue = deque(
        [
            (
                start_entity,
                [start_entity],
            )
        ]
    )

    visited = {start_entity}

    while queue:
        current_entity, current_path = (
            queue.popleft()
        )

        edges_used = len(current_path) - 1

        if edges_used >= max_edges:
            continue

        for neighbour in adjacency.get(
            current_entity,
            [],
        ):
            if neighbour in visited:
                continue

            new_path = (
                current_path
                + [neighbour]
            )

            if neighbour == end_entity:
                return new_path

            visited.add(neighbour)

            queue.append(
                (
                    neighbour,
                    new_path,
                )
            )

    return None


def get_relationship_between(
    first_entity: str,
    second_entity: str,
    relationships: pd.DataFrame,
) -> dict[str, str] | None:
    """Return relationship details between two entities."""

    direct_match = relationships[
        (
            relationships["Source"]
            .str.casefold()
            == first_entity.casefold()
        )
        &
        (
            relationships["Target"]
            .str.casefold()
            == second_entity.casefold()
        )
    ]

    if not direct_match.empty:
        row = direct_match.iloc[0]

        return {
            "Source": str(row["Source"]),
            "Relationship": str(
                row["Relationship"]
            ),
            "Target": str(row["Target"]),
            "Evidence": str(
                row["Evidence"]
            ),
            "Traversal": "forward",
        }

    reverse_match = relationships[
        (
            relationships["Source"]
            .str.casefold()
            == second_entity.casefold()
        )
        &
        (
            relationships["Target"]
            .str.casefold()
            == first_entity.casefold()
        )
    ]

    if not reverse_match.empty:
        row = reverse_match.iloc[0]

        return {
            "Source": str(row["Source"]),
            "Relationship": str(
                row["Relationship"]
            ),
            "Target": str(row["Target"]),
            "Evidence": str(
                row["Evidence"]
            ),
            "Traversal": "reverse",
        }

    return None


def describe_path(
    path: list[str],
    relationships: pd.DataFrame,
) -> list[dict[str, str]]:
    """Convert a graph path into explainable steps."""

    steps: list[dict[str, str]] = []

    for index in range(
        len(path) - 1
    ):
        current_entity = path[index]
        next_entity = path[index + 1]

        relationship_data = (
            get_relationship_between(
                current_entity,
                next_entity,
                relationships,
            )
        )

        if relationship_data is None:
            continue

        if (
            relationship_data["Traversal"]
            == "forward"
        ):
            arrow = "→"
        else:
            arrow = "←"

        steps.append(
            {
                "From": current_entity,
                "Arrow": arrow,
                "Relationship": (
                    relationship_data[
                        "Relationship"
                    ]
                ),
                "To": next_entity,
                "Evidence": (
                    relationship_data[
                        "Evidence"
                    ]
                ),
            }
        )

    return steps


def create_path_summary(
    path: list[str],
    relationships: pd.DataFrame,
) -> str:
    """Create a readable path summary."""

    if len(path) == 1:
        return path[0]

    parts = [path[0]]

    for index in range(
        len(path) - 1
    ):
        current_entity = path[index]
        next_entity = path[index + 1]

        relationship_data = (
            get_relationship_between(
                current_entity,
                next_entity,
                relationships,
            )
        )

        if relationship_data is None:
            parts.append(
                "— Connected To →"
            )

            parts.append(
                next_entity
            )

            continue

        relationship_name = (
            format_relationship_name(
                relationship_data[
                    "Relationship"
                ]
            )
        )

        if (
            relationship_data["Traversal"]
            == "forward"
        ):
            parts.append(
                f"— {relationship_name} →"
            )
        else:
            parts.append(
                f"← {relationship_name} —"
            )

        parts.append(
            next_entity
        )

    return " ".join(parts)


def collect_path_evidence(
    path: list[str],
    relationships: pd.DataFrame,
) -> list[str]:
    """Collect unique evidence sources."""

    evidence_sources: list[str] = []

    path_steps = describe_path(
        path,
        relationships,
    )

    for step in path_steps:
        evidence = step["Evidence"]

        if (
            evidence
            and evidence.casefold()
            != "nan"
            and evidence
            not in evidence_sources
        ):
            evidence_sources.append(
                evidence
            )

    return evidence_sources


# ==================================================
# DRUG RECOMMENDATION ENGINE
# ==================================================

def get_drug_recommendations(
    selected_disease: str,
    entities: pd.DataFrame,
    relationships: pd.DataFrame,
    max_edges: int = 4,
) -> list[dict[str, object]]:
    """Generate graph-derived drug recommendations."""

    adjacency = build_graph_adjacency(
        relationships
    )

    drug_names = (
        entities[
            entities["Type"]
            .str.casefold()
            == "drug"
        ]["Entity"]
        .drop_duplicates()
        .tolist()
    )

    recommendations: list[
        dict[str, object]
    ] = []

    for drug_name in drug_names:
        path = find_shortest_path(
            start_entity=drug_name,
            end_entity=selected_disease,
            adjacency=adjacency,
            max_edges=max_edges,
        )

        if path is None:
            continue

        path_steps = describe_path(
            path,
            relationships,
        )

        if not path_steps:
            continue

        is_direct_treatment = (
            len(path) == 2
            and path_steps[0][
                "Relationship"
            ].casefold()
            == "treats"
            and path_steps[0][
                "Arrow"
            ]
            == "→"
        )

        if is_direct_treatment:
            recommendation_type = (
                "Direct treatment relationship"
            )

            confidence_label = (
                "Direct graph evidence"
            )

            rank = 0

        else:
            recommendation_type = (
                "Mechanism-linked graph candidate"
            )

            confidence_label = (
                "Graph-derived mechanistic connection"
            )

            rank = len(path) - 1

        recommendations.append(
            {
                "Drug": drug_name,
                "Path": path,
                "Steps": path_steps,
                "Path Length": (
                    len(path) - 1
                ),
                "Recommendation Type": (
                    recommendation_type
                ),
                "Confidence Label": (
                    confidence_label
                ),
                "Evidence Sources": (
                    collect_path_evidence(
                        path,
                        relationships,
                    )
                ),
                "Rank": rank,
            }
        )

    recommendations.sort(
        key=lambda item: (
            int(item["Rank"]),
            str(item["Drug"]),
        )
    )

    return recommendations


# ==================================================
# INTERACTIVE GRAPH
# ==================================================

def get_nodes_within_depth(
    selected_entity: str,
    relationships: pd.DataFrame,
    depth: int,
) -> set[str]:
    """Return nearby nodes for focused graph mode."""

    adjacency = build_graph_adjacency(
        relationships
    )

    visited = {selected_entity}
    current_level = {selected_entity}

    for _ in range(depth):
        next_level: set[str] = set()

        for entity in current_level:
            next_level.update(
                adjacency.get(
                    entity,
                    [],
                )
            )

        next_level.difference_update(
            visited
        )

        if not next_level:
            break

        visited.update(
            next_level
        )

        current_level = next_level

    return visited


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
def find_shortest_entity_path(
    start_entity: str,
    end_entity: str,
    relationships: pd.DataFrame,
) -> list[str] | None:
    """
    Find the shortest connection between two biomedical entities.

    The graph is treated as undirected during path searching so that
    connections can be explored even when an edge points in the
    opposite biological direction.
    """

    if not start_entity or not end_entity:
        return None

    if start_entity == end_entity:
        return [start_entity]

    graph = nx.Graph()

    for _, relationship in relationships.iterrows():
        source = str(relationship["Source"]).strip()
        target = str(relationship["Target"]).strip()

        if source and target:
            graph.add_edge(source, target)

    if start_entity not in graph:
        return None

    if end_entity not in graph:
        return None

    try:
        return nx.shortest_path(
            graph,
            source=start_entity,
            target=end_entity,
        )

    except nx.NetworkXNoPath:
        return None

    except nx.NodeNotFound:
        return None

# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title(
    "🧬 SANJIVANI"
)

page = st.sidebar.radio(
    "Navigate",
    [
        "Home",
        "Search Entity",
        "Drug Recommendations",
        "Path Explorer",
        "Knowledge Graph",
        "Graph Analytics",
        "About",
    ],
)

st.sidebar.divider()

st.sidebar.caption(
    "Explainable biomedical "
    "evidence-graph prototype"
)


# ==================================================
# HOME PAGE
# ==================================================

if page == "Home":
    st.title(
        "🧬 SANJIVANI Evidence Graph"
    )

    st.write(
        "An explainable biomedical knowledge "
        "graph for exploring diseases, genes, "
        "proteins, pathways, protein complexes, "
        "drugs, and supporting evidence."
    )

    try:
        entities = load_entities()
        relationships = (
            load_relationships()
        )

        col1, col2, col3, col4 = (
            st.columns(4)
        )

        with col1:
            st.metric(
                "Biomedical Entities",
                len(entities),
            )

        with col2:
            st.metric(
                "Relationships",
                len(relationships),
            )

        with col3:
            st.metric(
                "Entity Types",
                entities[
                    "Type"
                ].nunique(),
            )

        with col4:
            st.metric(
                "Evidence Sources",
                relationships[
                    "Evidence"
                ].nunique(),
            )

        st.success(
            "SANJIVANI is connected "
            "successfully to entities.csv "
            "and relationships.csv."
        )

        st.subheader(
            "Explore the Platform"
        )

        left_column, right_column = (
            st.columns(2)
        )

        with left_column:
            with st.container(
                border=True
            ):
                st.subheader(
                    "🔍 Entity Explorer"
                )

                st.write(
                    "Search diseases, genes, "
                    "proteins, pathways, drugs, "
                    "and direct relationships."
                )

            with st.container(
                border=True
            ):
                st.subheader(
                    "💊 Drug Recommendations"
                )

                st.write(
                    "Discover direct treatments "
                    "and mechanism-linked "
                    "drug-to-disease paths."
                )

        with right_column:
            with st.container(
                border=True
            ):
                st.subheader(
                    "🕸️ Interactive Graph"
                )

                st.write(
                    "Explore a draggable and "
                    "zoomable biomedical network "
                    "with evidence tooltips."
                )

            with st.container(
                border=True
            ):
                st.subheader(
                    "📊 Graph Analytics"
                )

                st.write(
                    "Review entity distributions, "
                    "relationship types, and "
                    "evidence sources."
                )

        st.subheader(
            "Entity Distribution"
        )

        entity_counts = (
            entities["Type"]
            .value_counts()
            .rename_axis(
                "Entity Type"
            )
            .reset_index(
                name="Count"
            )
        )

        st.dataframe(
            entity_counts,
            width="stretch",
            hide_index=True,
        )

    except Exception as error:
        st.error(
            "Unable to load the "
            "SANJIVANI dataset: "
            f"{error}"
        )


# ==================================================
# SEARCH ENTITY PAGE
# ==================================================

elif page == "Search Entity":
    st.title(
        "🔍 Search Biomedical Entity"
    )

    try:
        entities = load_entities()
        relationships = (
            load_relationships()
        )

        st.caption(
            f"Searching across "
            f"{len(entities)} biomedical "
            f"entities and "
            f"{len(relationships)} "
            f"relationships."
        )

        search_term = st.text_input(
            "Enter an entity name "
            "or entity type",
            placeholder=(
                "Example: Metformin, "
                "Type 2 Diabetes, AMPK, "
                "Drug, Disease"
            ),
        )

        if not search_term:
            st.info(
                "Enter an entity name "
                "or type to begin searching."
            )

        else:
            matching_rows = entities[
                entities.astype(
                    str
                ).apply(
                    lambda row: (
                        row.str.contains(
                            search_term,
                            case=False,
                            na=False,
                            regex=False,
                        ).any()
                    ),
                    axis=1,
                )
            ]

            if matching_rows.empty:
                st.warning(
                    "No biomedical entity "
                    "was found for "
                    f'"{search_term}".'
                )

            else:
                st.success(
                    f"Found "
                    f"{len(matching_rows)} "
                    f"matching result(s)."
                )

                for _, entity_row in (
                    matching_rows.iterrows()
                ):
                    entity_name = str(
                        entity_row["Entity"]
                    )

                    entity_type = str(
                        entity_row["Type"]
                    )

                    entity_icon = (
                        get_entity_icon(
                            entity_type
                        )
                    )

                    with st.container(
                        border=True
                    ):
                        st.subheader(
                            f"{entity_icon} "
                            f"{entity_name}"
                        )

                        st.write(
                            "**Entity Type:** "
                            f"{entity_type}"
                        )

                        connected_rows = (
                            relationships[
                                (
                                    relationships[
                                        "Source"
                                    ].str.casefold()
                                    ==
                                    entity_name.casefold()
                                )
                                |
                                (
                                    relationships[
                                        "Target"
                                    ].str.casefold()
                                    ==
                                    entity_name.casefold()
                                )
                            ]
                        )

                        if connected_rows.empty:
                            st.info(
                                "No relationships "
                                "are currently recorded "
                                "for this entity."
                            )

                        else:
                            st.write(
                                "**Direct Connections:** "
                                f"{len(connected_rows)}"
                            )

                            for _, relation_row in (
                                connected_rows.iterrows()
                            ):
                                source = str(
                                    relation_row[
                                        "Source"
                                    ]
                                )

                                target = str(
                                    relation_row[
                                        "Target"
                                    ]
                                )

                                relationship = str(
                                    relation_row[
                                        "Relationship"
                                    ]
                                )

                                evidence = str(
                                    relation_row[
                                        "Evidence"
                                    ]
                                )

                                if (
                                    source.casefold()
                                    ==
                                    entity_name.casefold()
                                ):
                                    connected_entity = (
                                        target
                                    )

                                    direction = (
                                        "Outgoing"
                                    )

                                    connection_text = (
                                        f"{entity_name} "
                                        f"→ {target}"
                                    )

                                else:
                                    connected_entity = (
                                        source
                                    )

                                    direction = (
                                        "Incoming"
                                    )

                                    connection_text = (
                                        f"{source} "
                                        f"→ {entity_name}"
                                    )

                                connected_type = (
                                    get_entity_type(
                                        connected_entity,
                                        entities,
                                    )
                                )

                                connected_icon = (
                                    get_entity_icon(
                                        connected_type
                                    )
                                )

                                with st.expander(
                                    f"{connected_icon} "
                                    f"{connected_entity}"
                                ):
                                    st.write(
                                        "**Connection:** "
                                        f"{connection_text}"
                                    )

                                    st.write(
                                        "**Relationship:** "
                                        f"{format_relationship_name(relationship)}"
                                    )

                                    st.write(
                                        "**Direction:** "
                                        f"{direction}"
                                    )

                                    st.write(
                                        "**Connected Entity Type:** "
                                        f"{connected_type}"
                                    )

                                    st.write(
                                        "**Evidence Source:** "
                                        f"{evidence}"
                                    )

    except Exception as error:
        st.error(
            "Unable to search the "
            "biomedical graph: "
            f"{error}"
        )


# ==================================================
# DRUG RECOMMENDATIONS PAGE
# ==================================================

elif page == "Drug Recommendations":
    st.title(
        "💊 Explainable Drug "
        "Recommendation Engine"
    )

    st.write(
        "Select a disease to discover "
        "direct treatments and short "
        "mechanism-linked paths."
    )

    try:
        entities = load_entities()
        relationships = (
            load_relationships()
        )

        disease_entities = (
            entities[
                entities["Type"]
                .str.casefold()
                == "disease"
            ]["Entity"]
            .drop_duplicates()
            .sort_values()
            .tolist()
        )

        if not disease_entities:
            st.warning(
                "No disease entities were "
                "found in entities.csv."
            )

        else:
            selected_disease = (
                st.selectbox(
                    "Select a disease",
                    disease_entities,
                )
            )

            maximum_path_length = (
                st.slider(
                    "Maximum path length",
                    min_value=1,
                    max_value=5,
                    value=4,
                    help=(
                        "Smaller values produce "
                        "stricter and more closely "
                        "connected results."
                    ),
                )
            )

            recommendations = (
                get_drug_recommendations(
                    selected_disease=(
                        selected_disease
                    ),
                    entities=entities,
                    relationships=(
                        relationships
                    ),
                    max_edges=(
                        maximum_path_length
                    ),
                )
            )

            st.subheader(
                "Recommendations for "
                f"{selected_disease}"
            )

            if not recommendations:
                st.warning(
                    "No direct or "
                    "mechanism-linked drug "
                    "connections were found."
                )

            else:
                direct_results = [
                    result
                    for result
                    in recommendations
                    if result[
                        "Recommendation Type"
                    ]
                    ==
                    "Direct treatment relationship"
                ]

                mechanism_results = [
                    result
                    for result
                    in recommendations
                    if result[
                        "Recommendation Type"
                    ]
                    ==
                    "Mechanism-linked graph candidate"
                ]

                metric1, metric2, metric3 = (
                    st.columns(3)
                )

                with metric1:
                    st.metric(
                        "Total Candidates",
                        len(recommendations),
                    )

                with metric2:
                    st.metric(
                        "Direct Treatments",
                        len(direct_results),
                    )

                with metric3:
                    st.metric(
                        "Mechanism-Linked",
                        len(mechanism_results),
                    )

                if direct_results:
                    st.markdown(
                        "### Direct Treatment "
                        "Connections"
                    )

                    for result in (
                        direct_results
                    ):
                        with st.container(
                            border=True
                        ):
                            st.subheader(
                                f"💊 "
                                f"{result['Drug']}"
                            )

                            st.write(
                                "**Classification:** "
                                "Direct treatment "
                                "relationship"
                            )

                            st.write(
                                "**Explainable Path:**"
                            )

                            st.code(
                                create_path_summary(
                                    result["Path"],
                                    relationships,
                                ),
                                language=None,
                            )

                            evidence_sources = (
                                result[
                                    "Evidence Sources"
                                ]
                            )

                            if evidence_sources:
                                st.write(
                                    "**Supporting Evidence:** "
                                    + ", ".join(
                                        evidence_sources
                                    )
                                )

                            with st.expander(
                                "View path details"
                            ):
                                for (
                                    step_number,
                                    step,
                                ) in enumerate(
                                    result["Steps"],
                                    start=1,
                                ):
                                    st.write(
                                        f"**Step "
                                        f"{step_number}:** "
                                        f"{step['From']} "
                                        f"{step['Arrow']} "
                                        f"{step['To']}"
                                    )

                                    st.caption(
                                        "Relationship: "
                                        f"{format_relationship_name(step['Relationship'])}"
                                        " | Evidence: "
                                        f"{step['Evidence']}"
                                    )

                            st.success(
                                "A direct treatment "
                                "edge connects this "
                                "drug to the disease."
                            )

                if mechanism_results:
                    st.markdown(
                        "### Mechanism-Linked "
                        "Candidates"
                    )

                    st.caption(
                        "These results are inferred "
                        "from short paths in the "
                        "current curated graph."
                    )

                    for result in (
                        mechanism_results
                    ):
                        with st.container(
                            border=True
                        ):
                            st.subheader(
                                f"💊 "
                                f"{result['Drug']}"
                            )

                            st.write(
                                "**Classification:** "
                                "Mechanism-linked "
                                "graph candidate"
                            )

                            st.write(
                                "**Path Length:** "
                                f"{result['Path Length']} "
                                "relationship(s)"
                            )

                            st.write(
                                "**Explainable Path:**"
                            )

                            st.code(
                                create_path_summary(
                                    result["Path"],
                                    relationships,
                                ),
                                language=None,
                            )

                            evidence_sources = (
                                result[
                                    "Evidence Sources"
                                ]
                            )

                            if evidence_sources:
                                st.write(
                                    "**Supporting Evidence "
                                    "Sources:** "
                                    + ", ".join(
                                        evidence_sources
                                    )
                                )

                            with st.expander(
                                "View complete "
                                "biological path"
                            ):
                                for (
                                    step_number,
                                    step,
                                ) in enumerate(
                                    result["Steps"],
                                    start=1,
                                ):
                                    from_type = (
                                        get_entity_type(
                                            step[
                                                "From"
                                            ],
                                            entities,
                                        )
                                    )

                                    to_type = (
                                        get_entity_type(
                                            step[
                                                "To"
                                            ],
                                            entities,
                                        )
                                    )

                                    from_icon = (
                                        get_entity_icon(
                                            from_type
                                        )
                                    )

                                    to_icon = (
                                        get_entity_icon(
                                            to_type
                                        )
                                    )

                                    st.markdown(
                                        f"**Step "
                                        f"{step_number}**"
                                    )

                                    st.write(
                                        f"{from_icon} "
                                        f"**{step['From']}** "
                                        f"{step['Arrow']} "
                                        f"{to_icon} "
                                        f"**{step['To']}**"
                                    )

                                    st.caption(
                                        "Relationship: "
                                        f"{format_relationship_name(step['Relationship'])}"
                                        " | Evidence: "
                                        f"{step['Evidence']}"
                                    )

                                    if (
                                        step_number
                                        <
                                        len(
                                            result[
                                                "Steps"
                                            ]
                                        )
                                    ):
                                        st.divider()

                            st.info(
                                "This candidate was "
                                "identified by traversing "
                                "a short mechanistic path."
                            )

            st.warning(
                "Research and educational "
                "prototype only. These results "
                "are not medical advice."
            )

    except Exception as error:
        st.error(
            "Unable to generate drug "
            "recommendations: "
            f"{error}"
        )


# ==================================================
# KNOWLEDGE GRAPH PAGE
# ==================================================

elif page == "Path Explorer":
    st.title("🧭 Multi-Hop Path Explorer")

    st.write(
        "Find the shortest biological connection between two entities "
        "in the SANJIVANI knowledge graph."
    )
    overview = load_entities()

    with st.expander("📊 Knowledge Base Summary", expanded=False):

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Entities",
            len(overview)
        )

        col2.metric(
            "Entity Types",
            overview["Type"].nunique()
        )

        col3.metric(
            "Evidence Sources",
            load_relationships()["Evidence"].nunique()
        )

        st.dataframe(
            overview["Type"]
            .value_counts()
            .rename_axis("Entity Type")
            .reset_index(name="Count"),
            use_container_width=True,
            hide_index=True,
        )

    try:
        entities = load_entities()
        relationships = load_relationships()
        evidence_filter = st.multiselect(
            "Evidence Sources",
            sorted(
                relationships["Evidence"]
                .dropna()
                .unique()
                .tolist()
            ),
            default=sorted(
                relationships["Evidence"]
                .dropna()
                .unique()
                .tolist()
            ),
        )

        relationships = relationships[
            relationships["Evidence"].isin(
                evidence_filter
            )
        ]
    except Exception as error:
        st.error(
            f"The dataset could not be loaded: {error}"
        )
        st.stop()

    if entities.empty or relationships.empty:
        st.error(
            "The entity or relationship dataset is empty."
        )

    else:
        entity_names = sorted(
            entities["Entity"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        col1, col2 = st.columns(2)

        with col1:
            start_entity = st.selectbox(
                "Select Start Entity",
                entity_names,
                index=0,
                key="path_start_entity",
            )

        with col2:
            default_end_index = (
                1 if len(entity_names) > 1 else 0
            )

            end_entity = st.selectbox(
                "Select End Entity",
                entity_names,
                index=default_end_index,
                key="path_end_entity",
            )

        search_path = st.button(
            "Find Shortest Path",
            type="primary",
            use_container_width=True,
        )

        if search_path:
            if start_entity == end_entity:
                st.warning(
                    "Please select two different entities."
                )

            else:
                path = find_shortest_entity_path(
                    start_entity,
                    end_entity,
                    relationships,
                )

                if path is None:
                    st.error(
                        "No connection was found between "
                        "the selected entities."
                    )

                else:
                    st.success(
                        f"Path found with "
                        f"{len(path) - 1} "
                        "relationship step(s)."
                    )

                    st.subheader("Pathway")

                    st.markdown(
                        " → ".join(
                            f"**{entity}**"
                            for entity in path
                        )
                    )

                    (
                        metric_col1,
                        metric_col2,
                        metric_col3,
                    ) = st.columns(3)

                    metric_col1.metric(
                        "Path Length",
                        len(path) - 1,
                    )

                    metric_col2.metric(
                        "Entities",
                        len(path),
                    )

                    metric_col3.metric(
                        "Intermediate Entities",
                        max(len(path) - 2, 0),
                    )
                    explanation_sentences = []

                    for index in range(len(path) - 1):
                        current_entity = path[index]
                        next_entity = path[index + 1]

                        relationship_data = (
                            get_relationship_between(
                                current_entity,
                                next_entity,
                                relationships,
                            )
                        )

                        if relationship_data is None:
                            continue

                        relationship_name = (
                            format_relationship_name(
                                relationship_data[
                                    "Relationship"
                                ]
                            )
                        )

                        explanation_sentences.append(
                            f"{current_entity} "
                            f"{relationship_name.lower()} "
                            f"{next_entity}."
                        )

                    if explanation_sentences:
                        st.subheader(
                            "Biological Explanation"
                        )

                        st.info(
                            " ".join(
                                explanation_sentences
                            )
                        )

                    st.subheader(
                        "Relationship Evidence"
                    )

                    path_relationships = []

                    for index in range(
                        len(path) - 1
                    ):
                        current_entity = path[index]
                        next_entity = path[index + 1]

                        relationship_data = (
                            get_relationship_between(
                                current_entity,
                                next_entity,
                                relationships,
                            )
                        )

                        if relationship_data is None:
                            continue

                        path_relationships.append(
                            {
                                "From": current_entity,
                                "Relationship": (
                                    format_relationship_name(
                                        relationship_data[
                                            "Relationship"
                                        ]
                                    )
                                ),
                                "To": next_entity,
                                "Evidence": (
                                    relationship_data[
                                        "Evidence"
                                    ]
                                ),
                                "Traversal": (
                                    relationship_data[
                                        "Traversal"
                                    ]
                                ),
                            }
                        )

                    if path_relationships:
                        path_table = pd.DataFrame(
                            path_relationships
                        )

                        st.dataframe(
                            path_table,
                            use_container_width=True,
                            hide_index=True,
                        )

                        evidence_csv = path_table.to_csv(
                            index=False
                        ).encode("utf-8")

                        st.download_button(
                            label="📊 Download Evidence Table",
                            data=evidence_csv,
                            file_name=(
                                f"sanjivani_evidence_"
                                f"{start_entity}_to_"
                                f"{end_entity}.csv"
                            ),
                            mime="text/csv",
                            use_container_width=True,
                        )

                        confidence_score = 0

                        for step in path_relationships:
                            evidence = step["Evidence"]

                            if evidence == "DrugBank":
                                confidence_score += 5
                            elif evidence == "KEGG":
                                confidence_score += 5
                            elif evidence == "GeneCards":
                                confidence_score += 4
                            elif evidence == "UniProt":
                                confidence_score += 4
                            else:
                                confidence_score += 3

                        max_score = len(path_relationships) * 5

                        if confidence_score >= max_score * 0.8:
                            confidence_level = "🟢 High"
                        elif confidence_score >= max_score * 0.5:
                            confidence_level = "🟡 Moderate"
                        else:
                            confidence_level = "🔴 Low"

                        st.subheader("Path Confidence")

                        col1, col2 = st.columns(2)

                        with col1:
                            st.metric(
                                "Confidence Score",
                                f"{confidence_score}/{max_score}",
                            )

                        with col2:
                            st.metric(
                                "Confidence Level",
                                confidence_level,
                            )

                    else:
                        st.info(
                            "No detailed relationship "
                            "evidence was available."
                        )
                    report_generated_at = datetime.now().strftime(
                        "%d %B %Y, %I:%M %p"
                    )

                    path_report = f"""
SANJIVANI PATH EXPLORER REPORT

Generated On: {report_generated_at}

Start Entity: {start_entity}
End Entity: {end_entity}

Pathway:
{" -> ".join(path)}

Path Length: {len(path) - 1} relationship step(s)

Relationship Evidence:
"""

                    for step in path_relationships:
                        path_report += (
                            f"\n{step['From']} "
                            f"--[{step['Relationship']}]--> "
                            f"{step['To']}\n"
                            f"Evidence: {step['Evidence']}\n"
                            f"Traversal: {step['Traversal']}\n"
                        )

                    st.download_button(
                        label="📄 Download Path Report",
                        data=path_report,
                        file_name=(
                            f"sanjivani_path_"
                            f"{start_entity}_to_{end_entity}.txt"
                        ),
                        mime="text/plain",
                        use_container_width=True,
                    )
                    st.subheader(
                        "Interactive Path Graph"
                    )

                    path_graph_html = (
                        create_path_graph_html(
                            path,
                            entities,
                            relationships,
                        )
                    )

                    components.html(
                        path_graph_html,
                        height=650,
                        scrolling=True,
                    )

elif page == "Knowledge Graph":

    st.title(
        "🕸️ Interactive Knowledge Graph"
    )

    st.write(
        "Drag nodes, zoom in or out, "
        "hover over entities, and inspect "
        "relationship evidence."
    )

    try:
        entities = load_entities()
        relationships = (
            load_relationships()
        )

        graph_mode = st.radio(
            "Choose a graph view",
            [
                "Focused entity view",
                "Complete graph",
            ],
            horizontal=True,
        )

        selected_entity: str | None = None
        connection_depth = 2

        if (
            graph_mode
            == "Focused entity view"
        ):
            selected_entity = (
                st.selectbox(
                    "Search or choose a biomedical entity",
                    sorted(
                        entities[
                            "Entity"
                        ].tolist()
                    ),
                )
            )

            connection_depth = st.slider(
                "Connection depth",
                min_value=1,
                max_value=3,
                value=2,
                help=(
                    "Depth 1 displays direct "
                    "neighbours. Depth 2 or 3 "
                    "displays a wider network."
                ),
            )
            selected_entity_row = entities[
                entities["Entity"] == selected_entity
            ]

            entity_type = (
                selected_entity_row["Type"].iloc[0]
                if not selected_entity_row.empty
                else "Unknown"
            )

            source_column = (
                "Source"
                if "Source" in relationships.columns
                else "From"
            )

            target_column = (
                "Target"
                if "Target" in relationships.columns
                else "To"
            )

            connected_relationships = relationships[
                (
                    relationships[source_column]
                    == selected_entity
                )
                |
                (
                    relationships[target_column]
                    == selected_entity
                )
            ]

            evidence_sources = sorted(
                connected_relationships["Evidence"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            with st.expander(
                "📌 Selected Entity Quick Facts",
                expanded=True,
            ):
                fact_col1, fact_col2 = st.columns(2)

                fact_col1.metric(
                    "Entity",
                    selected_entity,
                )

                fact_col2.metric(
                    "Entity Type",
                    entity_type,
                )

                st.metric(
                    "Connected Relationships",
                    len(connected_relationships),
                )

                st.write(
                    "**Evidence Sources:** "
                    + (
                        ", ".join(evidence_sources)
                        if evidence_sources
                        else "No evidence available"
                    )
                )

        with st.spinner(
            "Building the interactive "
            "network..."
        ):
            (
                graph_html,
                visible_nodes,
                visible_edges,
            ) = create_interactive_graph_html(
                entities=entities,
                relationships=relationships,
                selected_entity=(
                    selected_entity
                ),
                depth=connection_depth,
            )

        metric1, metric2 = st.columns(2)

        with metric1:
            st.metric(
                "Visible Entities",
                visible_nodes,
            )

        with metric2:
            st.metric(
                "Visible Relationships",
                visible_edges,
            )

        components.html(
            graph_html,
            height=760,
            scrolling=True,
        )

        st.caption(
            "Node colours: red = disease, "
            "green = drug, purple = gene, "
            "blue = protein, cyan = protein "
            "complex, orange = pathway."
        )

        st.info(
            "Use the graph controls to zoom "
            "and move. Drag nodes to rearrange "
            "the network. Hover over nodes or "
            "edges to view details."
        )

        with st.expander(
            "View static graph image"
        ):
            graph_image = (
                get_graph_image()
            )

            if graph_image is not None:
                st.image(
                    str(graph_image),
                    caption=(
                        "SANJIVANI Static "
                        "Knowledge Graph"
                    ),
                    width="stretch",
                )

            else:
                st.caption(
                    "No static PNG graph image "
                    "is currently available."
                )

    except Exception as error:
        st.error(
            "Unable to build the "
            "interactive knowledge graph: "
            f"{error}"
        )


# ==================================================
# GRAPH ANALYTICS PAGE
# ==================================================

elif page == "Graph Analytics":
    st.title(
        "📊 Graph Analytics"
    )

    try:
        entities = load_entities()
        relationships = (
            load_relationships()
        )

        col1, col2, col3, col4 = (
            st.columns(4)
        )

        with col1:
            st.metric(
                "Total Entities",
                len(entities),
            )

        with col2:
            st.metric(
                "Total Relationships",
                len(relationships),
            )

        with col3:
            st.metric(
                "Entity Categories",
                entities[
                    "Type"
                ].nunique(),
            )

        with col4:
            st.metric(
                "Evidence Sources",
                relationships[
                    "Evidence"
                ].nunique(),
            )

        st.subheader(
            "Entity-Type Distribution"
        )

        type_counts = (
            entities["Type"]
            .value_counts()
            .rename_axis(
                "Entity Type"
            )
            .reset_index(
                name="Count"
            )
        )

        st.bar_chart(
            type_counts.set_index(
                "Entity Type"
            )
        )

        st.dataframe(
            type_counts,
            width="stretch",
            hide_index=True,
        )

        st.subheader(
            "Relationship Distribution"
        )

        relationship_counts = (
            relationships[
                "Relationship"
            ]
            .value_counts()
            .rename_axis(
                "Relationship"
            )
            .reset_index(
                name="Count"
            )
        )

        relationship_counts[
            "Relationship"
        ] = relationship_counts[
            "Relationship"
        ].apply(
            format_relationship_name
        )

        st.bar_chart(
            relationship_counts.set_index(
                "Relationship"
            )
        )

        st.dataframe(
            relationship_counts,
            width="stretch",
            hide_index=True,
        )

        st.subheader(
            "Evidence Sources"
        )

        evidence_counts = (
            relationships[
                "Evidence"
            ]
            .value_counts()
            .rename_axis(
                "Evidence Source"
            )
            .reset_index(
                name="Count"
            )
        )

        st.bar_chart(
            evidence_counts.set_index(
                "Evidence Source"
            )
        )

        st.dataframe(
            evidence_counts,
            width="stretch",
            hide_index=True,
        )

    except Exception as error:
        st.error(
            "Unable to calculate "
            "graph analytics: "
            f"{error}"
        )


# ==================================================
# ABOUT PAGE
# ==================================================

elif page == "About":
    st.title(
        "ℹ️ About SANJIVANI"
    )

    st.write(
        "SANJIVANI is an explainable "
        "biomedical evidence-graph platform "
        "designed to connect diseases, genes, "
        "proteins, pathways, protein complexes, "
        "drugs, and biomedical evidence."
    )

    st.subheader(
        "Current Capabilities"
    )

    st.markdown(
        """
        - Biomedical entity search
        - Direct relationship exploration
        - Disease-based drug recommendations
        - Multi-hop shortest-path exploration
        - Biological pathway explanation
        - Evidence-source filtering
        - Path confidence scoring
        - Interactive draggable knowledge graph
        - Selected entity quick facts
        - Entity and relationship analytics
        - Downloadable TXT path reports
        - Downloadable CSV evidence tables
        """
    )

    st.subheader(
        "Explainability"
    )

    st.write(
        "SANJIVANI does not present a drug "
        "name alone. It displays the graph "
        "path connecting the drug to a disease, "
        "including intermediate entities, "
        "relationship labels, and evidence."
    )

    st.subheader(
        "Data Sources Represented"
    )

    try:
        relationships = (
            load_relationships()
        )

        evidence_sources = sorted(
            relationships[
                "Evidence"
            ]
            .dropna()
            .unique()
            .tolist()
        )

        st.write(
            ", ".join(
                evidence_sources
            )
        )

    except Exception:
        st.write(
            "DrugBank, GeneCards, UniProt, "
            "Reactome, KEGG, and DisGeNET."
        )

    st.subheader(
        "Important Scientific Disclaimer"
    )

    st.info(
        "SANJIVANI is an educational and "
        "research prototype. Its graph-derived "
        "drug relationships must not be used "
        "as medical advice, prescriptions, "
        "or clinical guidance."
    )
    st.divider()

st.caption(
    "🧬 SANJIVANI v1.0 | "
    "Explainable Biomedical Knowledge Graph Platform"
)

st.caption(
    "Developed by Ishitta Sarkar"
)

st.caption(
    "© 2026 SANJIVANI"
)