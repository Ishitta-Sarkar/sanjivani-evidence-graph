# Source

Command-line graph:

- `graph_builder.py` stores relationships and finds a shortest undirected path
- `entity_loader.py` reads entity types
- `data_validator.py` checks the relationship CSV
- `graph_analytics.py` computes degree, density and hubs
- `graph_visualizer.py` writes the static PNG
- `drug_recommender.py` lists drugs connected to a disease

Shared score:

- `scoring.py` maps an evidence source to points and a High / Moderate / Low band

Web application:

- `loaders.py` reads the CSVs for Streamlit
- `entities.py` looks up type, colour and icon
- `explore.py` finds paths and drug candidates for the pages
- `interactive.py` builds the PyVis figures
- `ui/` holds one module per page
- `version.py` is the package version

`app.py` and `main.py` in the repository root are the two entry points.
