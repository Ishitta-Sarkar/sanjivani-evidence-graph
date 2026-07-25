def _find_exact_entity(graph, entity_name):
    """Find a stored entity name without requiring exact capitalization."""

    cleaned_name = entity_name.strip().casefold()

    for entity in graph.adjacency:
        if entity.casefold() == cleaned_name:
            return entity

    return None


def _is_drug(entity_name, entity_types):
    """Check whether an entity is typed as a drug."""

    entity_type = entity_types.get(
        entity_name,
        "Unknown",
    )

    return str(entity_type).casefold() == "drug"


def _format_path(path):
    """Convert a path into a readable explanation."""

    path_parts = []

    for step in path:
        if step["direction"] == "forward":
            path_parts.append(
                f"{step['source']} "
                f"--{step['relationship']}--> "
                f"{step['target']}"
            )
        else:
            path_parts.append(
                f"{step['source']} "
                f"<--{step['relationship']}-- "
                f"{step['target']}"
            )

    return " | ".join(path_parts)


def recommend_drugs(
    graph,
    disease_name,
    entity_types,
    maximum_path_length=5,
):
    """
    Find drugs connected to a disease through direct or short graph paths.

    Results are intended for educational graph analysis, not medical advice.
    """

    actual_disease = _find_exact_entity(
        graph,
        disease_name,
    )

    if actual_disease is None:
        return []

    recommendations = []

    for entity in graph.get_entities():
        if not _is_drug(
            entity,
            entity_types,
        ):
            continue

        path = graph.find_path(
            entity,
            actual_disease,
        )

        if not path:
            continue

        if len(path) > maximum_path_length:
            continue

        direct_treatment = (
            len(path) == 1
            and path[0]["relationship"].casefold() == "treats"
        )

        if direct_treatment:
            recommendation_type = "Direct treatment evidence"
        else:
            recommendation_type = "Mechanistic graph connection"

        evidence_sources = sorted(
            {
                step["evidence"]
                for step in path
                if step.get("evidence")
            },
            key=str.lower,
        )

        recommendations.append(
            {
                "drug": entity,
                "path_length": len(path),
                "recommendation_type": recommendation_type,
                "evidence_sources": evidence_sources,
                "path": path,
            }
        )

    recommendations.sort(
        key=lambda item: (
            item["path_length"],
            item["drug"].lower(),
        )
    )

    return recommendations


def display_recommendations(
    graph,
    disease_name,
    entity_types,
):
    """Display explainable graph-based drug suggestions."""

    actual_disease = _find_exact_entity(
        graph,
        disease_name,
    )

    print("\nDrug Recommendation")
    print("=" * 50)

    if actual_disease is None:
        print(f"Disease not found: {disease_name}")
        print("=" * 50)
        return

    recommendations = recommend_drugs(
        graph,
        actual_disease,
        entity_types,
    )

    print(f"Disease: {actual_disease}")
    print(
        "Note: Results are graph-based research suggestions, "
        "not medical advice."
    )

    if not recommendations:
        print("\nNo connected drugs were found.")
        print("=" * 50)
        return

    print("\nConnected drugs\n")

    for number, recommendation in enumerate(
        recommendations,
        start=1,
    ):
        evidence_text = ", ".join(
            recommendation["evidence_sources"]
        )

        print(f"{number}. {recommendation['drug']}")
        print(
            f"   Basis: "
            f"{recommendation['recommendation_type']}"
        )
        print(
            f"   Path length: "
            f"{recommendation['path_length']}"
        )
        print(f"   Evidence: {evidence_text}")
        print(
            f"   Explanation: "
            f"{_format_path(recommendation['path'])}"
        )
        print()

    print("=" * 50)