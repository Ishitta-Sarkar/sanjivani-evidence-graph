"""Schema checks for the relationship table."""

import csv
import io
from pathlib import Path

import pytest

from src.data_validator import validate_dataset
from src.entity_loader import load_entity_types
from src.graph_builder import BiomedicalGraph
from src.scoring import points_for_source


def _reader(text: str) -> csv.DictReader:
    return csv.DictReader(io.StringIO(text))


def test_validate_dataset_accepts_a_complete_row():
    rows = validate_dataset(
        _reader(
            "Source,Relationship,Target,Evidence\n"
            "A,treats,B,DrugBank\n"
        )
    )
    assert rows[0]["Evidence"] == "DrugBank"


def test_validate_dataset_rejects_an_empty_evidence_cell():
    with pytest.raises(ValueError, match="empty fields"):
        validate_dataset(
            _reader(
                "Source,Relationship,Target,Evidence\n"
                "A,treats,B,\n"
            )
        )


def test_blank_evidence_stored_by_the_graph_scores_zero():
    graph = BiomedicalGraph()
    graph.add_relationship("A", "related_to", "B", "  ")
    assert graph.relationships[0]["evidence"] == "Not specified"
    assert points_for_source(graph.relationships[0]["evidence"]) == 0


def test_entity_loader_reads_the_curated_types():
    data = Path(__file__).resolve().parents[1] / "data" / "entities.csv"
    types = load_entity_types(data)
    assert types["AMPK"] == "Protein Complex"
    assert len(types) == 71
