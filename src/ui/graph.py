"""Interactive knowledge-graph page."""

import streamlit as st
import streamlit.components.v1 as components

from src.interactive import create_interactive_graph_html
from src.loaders import get_graph_image, load_entities, load_relationships


def render() -> None:

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
