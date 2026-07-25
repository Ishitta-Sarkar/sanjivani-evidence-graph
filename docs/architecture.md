# SANJIVANI Architecture

```text
                 +----------------------+
                 | relationships.csv    |
                 +----------+-----------+
                            |
                            v
                  Dataset Validation
                            |
                            v
                  BiomedicalGraph
                            |
        +-------------------+-------------------+
        |                   |                   |
        v                   v                   v
 Connection Search      Path Finding      Visualization
        |                   |                   |
        +-------------------+-------------------+
                            |
                            v
                     User Interface
                         (main.py)
```