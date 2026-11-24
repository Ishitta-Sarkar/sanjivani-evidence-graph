"""Home page."""

import streamlit as st

from src.loaders import load_entities, load_relationships


def render() -> None:
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
