"""Numbers reported from the undirected graph summary."""

from pathlib import Path

from main import load_relationships
from src.entity_loader import load_entity_types
from src.graph_analytics import calculate_graph_statistics

ROOT = Path(__file__).resolve().parents[1]


def test_graph_summary_matches_the_curated_tables():
    graph = load_relationships(ROOT / "data" / "relationships.csv")
    entity_types = load_entity_types(ROOT / "data" / "entities.csv")
    stats = calculate_graph_statistics(graph, entity_types)

    assert stats["total_entities"] == 71
    assert stats["total_relationships"] == 74
    assert stats["entity_types"] == {
        "Disease": 14,
        "Drug": 13,
        "Gene": 13,
        "Pathway": 13,
        "Protein": 17,
        "Protein Complex": 1,
    }
    assert stats["average_degree"] == 2.08
    assert stats["graph_density"] == 0.0298
    assert stats["top_connected_entities"] == [
        ("Parkinson's Disease", 4),
        ("Alzheimer's Disease", 3),
        ("Angiotensin-Converting Enzyme", 3),
        ("Angiotensin-Converting Enzyme 2", 3),
        ("Asthma", 3),
    ]
