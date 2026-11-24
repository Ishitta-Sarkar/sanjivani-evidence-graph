"""The static figure writer still produces a PNG."""

from pathlib import Path

from main import load_relationships
from src.entity_loader import load_entity_types
from src.graph_visualizer import create_graph_visualization

ROOT = Path(__file__).resolve().parents[1]


def test_static_figure_is_written(tmp_path, capsys):
    graph = load_relationships(ROOT / "data" / "relationships.csv")
    entity_types = load_entity_types(ROOT / "data" / "entities.csv")
    output = tmp_path / "biomedical_graph.png"

    create_graph_visualization(graph, entity_types, output_file=output)

    assert output.is_file()
    assert output.stat().st_size > 0
    assert str(output) in capsys.readouterr().out
