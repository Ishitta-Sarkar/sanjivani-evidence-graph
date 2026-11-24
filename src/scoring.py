"""Heuristic confidence for a path, from the evidence source on each edge.

The score makes the curation behind a path visible. It is not a probability,
it is not fitted to an outcome, and it is not a clinical ranking.

Points follow how the source curates a statement:

- DrugBank, Reactome and KEGG score 5. These are expert-curated databases
  of drugs, peer-reviewed reactions, and pathway maps. Reactome previously
  scored 3, in the same bucket as a source the table did not name.
- UniProt scores 4. It is an expert-reviewed protein record, which is
  stronger than an aggregator and is not itself a pathway or drug review.
- DisGeNET and GeneCards score 3. DisGeNET mixes expert curation and text
  mining. GeneCards is a gene-centric aggregator, so it no longer scores 4
  and no longer outranks Reactome. DisGeNET previously fell in the unnamed
  bucket, which was also 3.
- Any other label, a blank cell, or a missing value scores 0. Previously
  these received 3.

``score`` is the sum of the edge points. ``maximum`` is 5 times the number
of edges. The path is High when ``score`` is at least 80% of ``maximum``,
Moderate when it is at least 50%, and Low otherwise. A path with no edges
is Low.
"""

from dataclasses import dataclass
from typing import Sequence

EVIDENCE_POINTS = {
    "DrugBank": 5,
    "Reactome": 5,
    "KEGG": 5,
    "UniProt": 4,
    "DisGeNET": 3,
    "GeneCards": 3,
}

MAX_POINTS_PER_EDGE = 5
HIGH_THRESHOLD = 0.8
MODERATE_THRESHOLD = 0.5

_UNSCORED = {"", "nan", "none", "null", "not specified"}

_LABELS = {
    "High": "🟢 High",
    "Moderate": "🟡 Moderate",
    "Low": "🔴 Low",
}


@dataclass(frozen=True)
class PathScore:
    """A path score and the band it falls in."""

    score: int
    maximum: int
    level: str

    @property
    def label(self) -> str:
        """Band name with the marker used in the web interface."""

        return _LABELS[self.level]


def points_for_source(evidence: object) -> int:
    """Return the weight of one evidence label.

    Matching is exact, after stripping whitespace. An empty value and any
    label that is not in ``EVIDENCE_POINTS`` score 0.
    """

    if evidence is None:
        return 0

    text = str(evidence).strip()

    if text.casefold() in _UNSCORED:
        return 0

    return EVIDENCE_POINTS.get(text, 0)


def score_sources(sources: Sequence[object]) -> PathScore:
    """Score a path from the evidence label on each edge, in path order."""

    labels = list(sources)
    score = sum(points_for_source(label) for label in labels)
    maximum = MAX_POINTS_PER_EDGE * len(labels)

    if maximum == 0 or score < maximum * MODERATE_THRESHOLD:
        level = "Low"
    elif score < maximum * HIGH_THRESHOLD:
        level = "Moderate"
    else:
        level = "High"

    return PathScore(score=score, maximum=maximum, level=level)
