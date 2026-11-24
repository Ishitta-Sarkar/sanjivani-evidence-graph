# Data

`entities.csv` and `relationships.csv` are a hand-curated demonstration graph. They are not a dump of a public knowledge base. Rows do not yet carry stable identifiers (UniProt accessions, DrugBank IDs, Reactome stable IDs) or an access date.

## entities.csv

| Column | Meaning |
|---|---|
| Entity | Display name used as a graph node |
| Type | Disease, Gene, Protein, Protein Complex, Pathway, or Drug |

## relationships.csv

| Column | Meaning |
|---|---|
| Source | Start entity. The name matches `entities.csv` |
| Relationship | `associated_with`, `encodes`, `participates_in`, `related_to`, `targets`, `treats`, or `binds_to` |
| Target | End entity |
| Evidence | Database the statement was taken from: DrugBank, UniProt, Reactome, KEGG, GeneCards, or DisGeNET |

The evidence cell names the database, not a record or a paper. DrugBank content is only summarised here. Reuse of DrugBank data is covered by DrugBank's own licence, which is separate from the MIT licence on this code.
