"""Drug-repurposing exploration page."""

import streamlit as st

from src.entities import (
    format_relationship_name,
    get_entity_icon,
    get_entity_type,
)
from src.explore import create_path_summary, get_drug_recommendations
from src.loaders import load_entities, load_relationships
from src.scoring import score_sources


def render() -> None:
    st.title(
        "💊 Explainable Drug "
        "Recommendation Engine"
    )

    st.write(
        "Select a disease to discover "
        "direct treatments and short "
        "mechanism-linked paths."
    )

    st.caption(
        "Path confidence uses the same evidence weights as "
        "Path Explorer. It is a heuristic, not a probability "
        "or a clinical ranking."
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

                            card_score = score_sources(
                                [
                                    step["Evidence"]
                                    for step in result["Steps"]
                                ]
                            )
                            st.write(
                                "**Path confidence:** "
                                f"{card_score.score}/"
                                f"{card_score.maximum} "
                                f"({card_score.level})"
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

                            card_score = score_sources(
                                [
                                    step["Evidence"]
                                    for step in result["Steps"]
                                ]
                            )
                            st.write(
                                "**Path confidence:** "
                                f"{card_score.score}/"
                                f"{card_score.maximum} "
                                f"({card_score.level})"
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
