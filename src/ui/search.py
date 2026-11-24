"""Entity search page."""

import streamlit as st

from src.entities import (
    format_relationship_name,
    get_entity_icon,
    get_entity_type,
)
from src.loaders import load_entities, load_relationships


def render() -> None:
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
