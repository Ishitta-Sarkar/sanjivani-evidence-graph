import pandas as pd
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"


def test_relationship_schema():
    df = pd.read_csv(DATA / "relationships.csv")
    assert list(df.columns) == ["Source", "Relationship", "Target", "Evidence"]
    assert df[["Source", "Relationship", "Target"]].notna().all().all()


def test_all_edge_endpoints_are_typed_entities():
    ents = set(pd.read_csv(DATA / "entities.csv")["Entity"])
    rel = pd.read_csv(DATA / "relationships.csv")
    missing = (set(rel.Source) | set(rel.Target)) - ents
    assert not missing, f"untyped entities: {missing}"


def test_evidence_present_and_known():
    rel = pd.read_csv(DATA / "relationships.csv")
    known = {"DrugBank", "UniProt", "Reactome", "KEGG", "GeneCards", "DisGeNET"}
    assert rel["Evidence"].notna().all()
    assert set(rel["Evidence"]) <= known


def test_no_blank_lines():
    for f in ("entities.csv", "relationships.csv"):
        lines = (DATA / f).read_text().splitlines()
        assert all(l.strip() for l in lines), f"blank lines in {f}"
