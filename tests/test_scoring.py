"""Tests for the path-confidence weights."""

from pathlib import Path

import pandas as pd

from src.scoring import EVIDENCE_POINTS, points_for_source, score_sources

DATA = Path(__file__).resolve().parents[1] / "data"


def test_weight_table_covers_every_recorded_source():
    recorded = set(pd.read_csv(DATA / "relationships.csv")["Evidence"])
    assert recorded == set(EVIDENCE_POINTS)


def test_curated_pathway_and_drug_sources_score_five():
    for source in ("DrugBank", "Reactome", "KEGG"):
        assert points_for_source(source) == 5


def test_uniprot_scores_four():
    assert points_for_source("UniProt") == 4


def test_aggregator_and_mixed_sources_score_three():
    assert points_for_source("GeneCards") == 3
    assert points_for_source("DisGeNET") == 3


def test_unknown_and_empty_sources_score_zero():
    for value in (None, "", "   ", "nan", "Not specified", "PubMed", "drugbank"):
        assert points_for_source(value) == 0


def test_bands_follow_the_published_thresholds():
    assert score_sources(["UniProt"]).level == "High"  # 4/5
    assert score_sources(["GeneCards"]).level == "Moderate"  # 3/5
    assert score_sources(["DrugBank", ""]).level == "Moderate"  # 5/10
    assert score_sources(["PubMed"]).level == "Low"  # 0/5
    assert score_sources([]).level == "Low"
    assert score_sources([]).maximum == 0


def test_score_is_the_sum_of_edge_weights():
    scored = score_sources(["DrugBank", "KEGG", "KEGG"])
    assert (scored.score, scored.maximum, scored.level) == (15, 15, "High")
    assert scored.label == "🟢 High"
