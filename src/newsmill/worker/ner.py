"""Named Entity Recognition (NER) using SpaCy."""

from __future__ import annotations

import logging
import threading

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

#: Entity labels that are stored in the database.
SUPPORTED_LABELS = frozenset({"PER", "ORG", "LOC", "MISC"})
#: SpaCy Russian model used for NER.
SPACY_MODEL = "ru_core_news_md"

_lock = threading.Lock()
_nlp = None


class EntityExtraction(BaseModel):
    """A single aggregated named entity.

    Attributes:
        text: Normalized entity text (title case).
        label: Entity label (PER, ORG, LOC, MISC).
        count: Number of occurrences in the news item.
    """

    text: str = Field(..., description="Normalized entity text")
    label: str = Field(..., description="Entity label")
    count: int = Field(1, ge=1, description="Occurrences count")


def get_nlp():
    """Load and return the shared SpaCy pipeline.

    The model is loaded once and reused. Loading is thread-safe and failures
    are logged without raising.

    Returns:
        The loaded SpaCy ``Language`` pipeline, or ``None`` if loading failed.
    """
    global _nlp
    if _nlp is None:
        with _lock:
            if _nlp is None:
                try:
                    import spacy

                    _nlp = spacy.load(SPACY_MODEL)
                    logger.info("Loaded SpaCy model %s", SPACY_MODEL)
                except Exception:
                    logger.exception("Failed to load SpaCy model %s", SPACY_MODEL)
                    _nlp = None
    return _nlp


def _normalize_label(label: str) -> str:
    """Map SpaCy label to a canonical stored label.

    Russian models use ``PER`` while English models use ``PERSON``; both are
    mapped to ``PER``. GPE is treated as a location.

    Args:
        label: The raw SpaCy entity label.

    Returns:
        A canonical label within ``SUPPORTED_LABELS``.
    """
    if label == "PERSON":
        return "PER"
    if label == "GPE":
        return "LOC"
    return label


def _aggregate(entities: list[tuple[str, str]]) -> list[EntityExtraction]:
    """Aggregate entity occurrences by (normalized text, label).

    Args:
        entities: Iterable of ``(text, label)`` tuples.

    Returns:
        A list of aggregated :class:`EntityExtraction` records.
    """
    counts: dict[tuple[str, str], int] = {}
    for text, label in entities:
        if label not in SUPPORTED_LABELS:
            continue
        key = (text, label)
        counts[key] = counts.get(key, 0) + 1

    return [
        EntityExtraction(text=text, label=label, count=count)
        for (text, label), count in sorted(
            counts.items(), key=lambda kv: (kv[0][1], kv[0][0])
        )
    ]


def extract_entities(title: str, text: str) -> list[EntityExtraction]:
    """Extract and aggregate named entities from a news item.

    Analyzes both the title and the body text with the shared SpaCy pipeline.

    Args:
        title: The news headline.
        text: The news body text.

    Returns:
        A list of aggregated :class:`EntityExtraction` records. Returns an
        empty list if the model is unavailable or processing fails.
    """
    nlp = get_nlp()
    if nlp is None:
        logger.warning("SpaCy model unavailable; skipping entity extraction")
        return []

    try:
        raw_entities: list[tuple[str, str]] = []
        for doc in nlp.pipe([title, text]):
            for ent in doc.ents:
                label = _normalize_label(ent.label_)
                if label in SUPPORTED_LABELS:
                    raw_entities.append((ent.text.strip(), label))
        return _aggregate(raw_entities)
    except Exception:
        logger.exception("Failed to extract entities; skipping NER for item")
        return []
