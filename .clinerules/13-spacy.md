# SpaCy NER Rules

## Purpose
SpaCy is used for Named Entity Recognition (NER) in the Worker service. It extracts named entities (persons, organizations, locations, etc.) from Russian news headlines and body text.

## Model Setup
- Use Russian-language SpaCy models: `ru_core_news_sm` or `ru_core_news_md`.
- Download the model with: `python -m spacy download ru_core_news_sm` (or `ru_core_news_md`).
- Load the model once at Worker startup using `spacy.load("ru_core_news_md")` (prefer the larger model for better accuracy).

## Entity Extraction
- Run the SpaCy pipeline on both `title` and `text` fields of each news item.
- Extract entities with the following labels (common Russian NER labels):
  - `PER` — person names
  - `ORG` — organizations
  - `LOC` — locations (cities, countries, regions)
  - `MISC` — miscellaneous named entities
- Collect all entities from both fields into a single list.

## Entity Counting
- Count occurrences of each unique entity (case-insensitive) within a single news item.
- For each unique entity, store:
  - `text` — the entity text (normalized to title case)
  - `label` — the entity label (PER, ORG, LOC, etc.)
  - `count` — number of occurrences in the news item
- Write the aggregated entity counts to the `entities` table.

## Error Handling
- Handle SpaCy processing errors gracefully (log the error, skip entity extraction for that item).
- Do not crash the Worker if the SpaCy model fails to process a single message.
- Validate that the model is loaded successfully on startup; log a warning if not.

## Performance
- Load the SpaCy model once and reuse the pipeline for all messages.
- Do not reload the model for each message — keep it in memory as a singleton.
- Use `nlp.pipe()` for batch processing if multiple messages need processing at once.