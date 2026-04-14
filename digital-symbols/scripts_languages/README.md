# Scripts ↔ Languages

Two independent sources, fetched and compared.

## Sources

**Wikidata** — SPARQL query against query.wikidata.org
- Property `P282` (writing system) links language → script
- `P506` = ISO 15924 script code, `P220` = ISO 639-3, `P218` = ISO 639-1
- Coverage: broad, includes historical and constructed scripts, uneven for minority languages
- File: `wikidata_query.sparql` (runnable in the browser UI)

**Unicode CLDR** — `supplementalData.xml` `<languageData>` block
- Each `<language>` entry lists its `scripts` and a `primary`/`secondary` status
- Coverage: authoritative for living/widely-used languages, sparse for historical
- Source: https://github.com/unicode-org/cldr (main branch)

## Usage

```
pip install requests
python fetch_all.py
```

Outputs land in `./data/`:
- `wikidata_pairs.json` — raw SPARQL rows
- `cldr_pairs.json` — (language, script, status) triples
- `cldr_language_names.json`, `cldr_script_names.json` — English labels
- `comparison.json` — set overlap keyed on (ISO 639, ISO 15924)
- `comparison.csv` — flat long table, one row per (source, lang, script)

## Notes on comparison

Intersection is computed on `(ISO 639-3 or 639-1, ISO 15924)`. Rows missing
either code are excluded from the set math but still appear in the CSV.
Expect Wikidata to have many more pairs (historical scripts, minority
languages, reconstructions); CLDR's extras tend to be locale/script
associations Wikidata hasn't modeled yet. Treat disagreements as a to-do
list, not an error.
