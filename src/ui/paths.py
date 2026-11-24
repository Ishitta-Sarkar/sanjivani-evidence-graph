"""Multi-hop path explorer page."""

from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from src.entities import format_relationship_name
from src.explore import (
    find_shortest_entity_path,
    get_relationship_between,
)
from src.interactive import create_path_graph_html
from src.loaders import load_entities, load_relationships
from src.scoring import score_sources


def render() -> None:
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
            width="stretch",
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
            width="stretch",
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

                    scored = None

                    if path_relationships:
                        path_table = pd.DataFrame(
                            path_relationships
                        )

                        st.dataframe(
                            path_table,
                            width="stretch",
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
                            width="stretch",
                        )

                        scored = score_sources(
                            [
                                step["Evidence"]
                                for step in path_relationships
                            ]
                        )

                        confidence_score = scored.score
                        max_score = scored.maximum
                        confidence_level = scored.label

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

                        st.caption(
                            "Heuristic score from the evidence source on "
                            "each edge: DrugBank, Reactome and KEGG = 5; "
                            "UniProt = 4; DisGeNET and GeneCards = 3; "
                            "any other or empty source = 0. "
                            "High is at least 80% of the maximum "
                            "(5 per edge), Moderate at least 50%, "
                            "otherwise Low. This is not a probability."
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

                    if scored is not None:
                        path_report += (
                            f"\nPath confidence: "
                            f"{scored.score}/{scored.maximum} "
                            f"({scored.level})\n"
                        )

                    st.download_button(
                        label="📄 Download Path Report",
                        data=path_report,
                        file_name=(
                            f"sanjivani_path_"
                            f"{start_entity}_to_{end_entity}.txt"
                        ),
                        mime="text/plain",
                        width="stretch",
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
