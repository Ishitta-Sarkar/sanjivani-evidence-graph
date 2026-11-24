# Changelog

All notable changes to SANJIVANI Evidence Graph are documented here.

## [1.0.1] - 2026-11-24

### Added

- MIT licence (`LICENSE`). The README had reserved all rights, `CITATION.cff` already said MIT, and the licence file was missing.
- ORCID `https://orcid.org/0009-0008-1028-6010` and the public app URL in `CITATION.cff`.
- Pinned `requirements.txt` (Streamlit 1.67.0, NetworkX 3.7, pandas 2.3.3, matplotlib 3.11.2, PyVis 0.3.2) and `requirements-dev.txt`.
- Pytest suite for the tables, graph construction, path search, evidence weights and analytics.
- GitHub Actions workflow that lints with Ruff and runs the tests on Python 3.12.
- `src/scoring.py`, the single definition of the path confidence score, used by the web app and the command line.
- Streamlit pages moved into `src/ui/`. `app.py` only dispatches the sidebar.
- Daily workflow that requests the public Streamlit URL.

### Changed

- Path confidence weights. DrugBank, Reactome and KEGG score 5; UniProt scores 4; DisGeNET and GeneCards score 3; an unrecognised or empty source scores 0. Reactome previously scored 3, with any source the table did not name. GeneCards previously scored 4. The bands are unchanged: High at or above 80% of 5 points per edge, Moderate at or above 50%, otherwise Low.
- The command line, the drug-candidate cards and the downloaded path report now show that score.
- Empty lines removed from `data/entities.csv` (8 lines) and `data/relationships.csv` (8 lines). The tables are still 71 entities and 74 relationships.

## [1.0.0] - 2026-07-26

### Added

- Biomedical knowledge graph
- CSV entity loader
- Relationship loader
- Dataset validation
- Direct connection search
- Shortest path discovery
- Case-insensitive search
- Graph visualization
- Project documentation
- Architecture documentation
