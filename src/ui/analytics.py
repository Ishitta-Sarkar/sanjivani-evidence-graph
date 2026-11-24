"""Graph analytics page."""

import streamlit as st

from src.entities import format_relationship_name
from src.loaders import load_entities, load_relationships


def render() -> None:
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
