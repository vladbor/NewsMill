# YAML Configuration Rules

## Purpose
The `newsfeeds.yaml` file contains the list of RSS feeds that the Monitor service polls periodically.

## File Format
- The file must be named `newsfeeds.yaml` and placed at the project root.
- The file contains a single top-level key `newsfeeds` with a list of dictionaries.
- Each dictionary has one key-value pair: `"Agency Name": "RSS URL"`.
- Supported agencies: RIA Novosti, TASS, Kommersant.

## Example Structure
```yaml
newsfeeds:
  - "RIA Novosti": "https://ria.ru/export/rss2/archive/index.xml"
  - "TASS": "https://tass.ru/rss/v2.xml"
  - "Kommersant": "https://www.kommersant.ru/RSS/news.xml"
```

## Parsing
- Use `PyYAML` (`yaml.safe_load()`) to parse the configuration file.
- Load the file at Monitor startup or lazily on first poll.
- Validate that the parsed structure matches the expected format.
- Handle missing or malformed `newsfeeds.yaml` gracefully (log error, fall back to defaults or exit).

## Integration
- The Monitor service reads `newsfeeds.yaml` to determine which RSS feeds to poll.
- Each feed is polled in sequence during the periodic polling cycle.
- The `source` field in published messages is taken from the agency name in the YAML file.