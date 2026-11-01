# Data

`eurovision_features.xlsx` is the six-sheet input used in the reported experiments.

| Dataset | Coverage | Rows |
|---|---|---:|
| A: all finalists | 2008–2025 | 437 |
| A: matched market sample | 2015–2025 | 259 |
| B: audience versus jury | 2016–2025 | 232 |
| C: national winners | 2016–2025 | 8,770 candidates in 349 national votes |

2020 is absent. C excludes self-votes, Rest of the World and San Marino's
substituted televotes, while retaining national voters outside the final.

## Frozen sources

`sources/reproduction_manifest.json` lists every input's SHA-256, URL where
available, acquisition record and the expected output CSV hashes. Internal source
filenames are preserved because the parsers and checks refer to those paths.

- EurovisionAPI: pinned contest, participant and voting data.
- Official Scoreboard snapshots and Wikipedia tables: result cross-checks.
- Song Science: published language, audio and lyric measurements.
- Dated running-order publications and an extraction ledger.
- Natural Earth v5.1.2: capitals and shared land borders.
- Eurovisionworld: archived five-bookmaker winner prices.

Notebook 01 contains the parsers and rebuilds the tables without reading the
ready-to-use workbook. Some web pages were collected through a browser; frozen
snapshots reproduce those inputs, not the past state of the live websites.
Song features are used as published, not re-extracted from recordings. Archived
odds measurement times are unknown; acquisition time is not a quote timestamp.
