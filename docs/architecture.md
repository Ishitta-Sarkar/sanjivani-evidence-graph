# SANJIVANI architecture

Two interfaces read the same tables.

```text
data/entities.csv          data/relationships.csv
        |                            |
        |                            +---- data_validator.py (command line)
        |                            |
        +-- entity_loader.py         +-- graph_builder.BiomedicalGraph
        |                            |         |
        |                            |         +-- main.py
        |                            |         |     search, paths, analytics,
        |                            |         |     drug suggestions, static figure
        |                            |         |
        |                            |         +-- scoring.score_sources
        |                            |
        +-- loaders.py (web) --------+-- explore.py (web path search)
                                     |         |
                                     |         +-- scoring.score_sources
                                     |
                                     +-- interactive.py (PyVis)
                                               |
                                               +-- src/ui/*.py
                                                         |
                                                         +-- app.py (sidebar)
```

`BiomedicalGraph.find_path` (command line) and `find_shortest_entity_path` (web Path Explorer) both walk the relationships as an undirected graph and return a shortest path. Drug suggestions on the web page stop at a caller-chosen number of edges. The command-line suggester uses `drug_recommender.py` and the same graph object.

`graph_analytics.py` reports entity counts, average degree, density and the highest-degree nodes. The web Graph Analytics page instead shows pandas value counts for types, relationship labels and evidence sources. Both are descriptive. Neither fits a model.

`scoring.py` is the only place that assigns points to an evidence source. The web pages and the command line call it. The weights and the 80% / 50% bands are documented in the README.
