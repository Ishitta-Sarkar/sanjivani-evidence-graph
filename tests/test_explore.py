"""Path finding on the curated graph, from both interfaces."""

from pathlib import Path

import pandas as pd

from main import load_relationships
from src.explore import find_shortest_entity_path, get_drug_recommendations
from src.loaders import load_entities
from src.scoring import score_sources

DATA = Path(__file__).resolve().parents[1] / "data"


def test_metformin_reaches_type_2_diabetes_in_three_curated_steps():
    graph = load_relationships(DATA / "relationships.csv")
    path = graph.find_path("metformin", "type 2 diabetes")
    evidences = [step["evidence"] for step in path]
    nodes = [path[0]["source"]] + [step["target"] for step in path]

    assert nodes == [
        "Metformin",
        "AMPK",
        "Glucose Metabolism",
        "Type 2 Diabetes",
    ]
    assert evidences == ["DrugBank", "KEGG", "KEGG"]
    assert score_sources(evidences).level == "High"


def test_olaparib_has_a_direct_treatment_edge():
    graph = load_relationships(DATA / "relationships.csv")
    path = graph.find_path("Olaparib", "Breast Cancer")
    assert len(path) == 1
    assert path[0]["relationship"] == "treats"
    assert path[0]["evidence"] == "DrugBank"
    assert score_sources([path[0]["evidence"]]).level == "High"


def test_insulin_has_no_path_to_alzheimers_disease():
    graph = load_relationships(DATA / "relationships.csv")
    assert graph.find_path("Insulin", "Alzheimer's Disease") == []


def test_app_shortest_path_matches_the_command_line_graph():
    relationships = pd.read_csv(DATA / "relationships.csv")
    nodes = find_shortest_entity_path(
        "Metformin",
        "Type 2 Diabetes",
        relationships,
    )
    assert nodes == [
        "Metformin",
        "AMPK",
        "Glucose Metabolism",
        "Type 2 Diabetes",
    ]
    assert (
        find_shortest_entity_path(
            "Insulin",
            "Alzheimer's Disease",
            relationships,
        )
        is None
    )


def test_breast_cancer_recommendation_is_the_direct_olaparib_edge():
    entities = load_entities()
    relationships = pd.read_csv(DATA / "relationships.csv")
    recommendations = get_drug_recommendations(
        "Breast Cancer",
        entities,
        relationships,
    )
    assert [item["Drug"] for item in recommendations] == ["Olaparib"]
    assert recommendations[0]["Recommendation Type"] == (
        "Direct treatment relationship"
    )
    assert score_sources(
        [step["Evidence"] for step in recommendations[0]["Steps"]]
    ).level == "High"
