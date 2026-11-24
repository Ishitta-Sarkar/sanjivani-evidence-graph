"""About page."""

import streamlit as st

from src.loaders import load_relationships


def render() -> None:
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
