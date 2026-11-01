# Eurovision forecasting

**Nikita Nazarov · Ivan Tanaev**

Bayesian forecasts of three Eurovision Grand Final outcomes: a top-ten finish,
a better audience rank than jury rank, and the winner of each national televote.
We compare country-history baselines, feature models and hierarchical extensions,
with and without bookmaker odds on the same observations.

**[Read the report](report/eurovision_report.pdf)** · [Presentation](Eurovision_Final.pdf) · [Data sources](data/README.md)

## Main findings

Expanding-window evaluation uses 2021–2024; 2025 is reported separately.
Adding archived odds reduces development top-ten Brier loss by about 49% and
national-winner log loss by 33–37%. It contributes little to audience–jury
prediction, where the country-history baseline performs best. The 2025 national
winner results depend on the metric: the best log-loss model is not the best
Brier or top-choice model.

**Odds timing is unverified.** Retrieval dates do not establish when the quoted
prices were measured. Market results are retrospective and do not establish
performance at the intended noon cutoff. The no-odds comparison was added after
the original presentation; the report explains this chronology.

## Where to start

| Path | Contents |
|---|---|
| `notebooks/01_rebuild_dataset.ipynb` | Offline reconstruction from 734 checked source files; 21 CSV checks and 46 data tests |
| `notebooks/02_explore_dataset.ipynb` | Data coverage, song features, country histories and geography, with saved plots |
| `notebooks/03_top10_rankings.ipynb` | A: Plackett–Luce ranking models |
| `notebooks/04_audience_vs_jury.ipynb` | B: Beta–Bernoulli baseline and Bayesian probit |
| `notebooks/05_national_televote_winners.ipynb` | C: categorical choice and directed pair effects |
| `data/` | Ready-to-use workbook and frozen original sources |
| `results/` | Saved market forecasts and completed no-odds notebooks; [details](results/README.md) |
| `report/` | PDF, LaTeX, figures, numerical evidence and figure-generation scripts |

## Run locally

Use Python 3.11 or 3.12. From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
jupyter lab
```

The model notebooks find the repository root automatically. They read
`data/eurovision_features.xlsx` and write new runs to `results/generated/`.
The default is `EXPERIMENT = "market"`; set it to `"matched_core"` in the
configuration cell to remove odds while keeping the same observations.
A's `"full_core"` experiment uses a longer history and is not the matched ablation.

Model fitting uses four NUTS chains and can take substantial time, especially for C.
Saved results can be inspected without running the models.

### Rebuild the data

Run notebook 01, or:

```bash
python -m pip install -r requirements-data.txt
python scripts/rebuild_data.py
```

The offline build writes to `build/data/`, checks the frozen CSV hashes and runs
the original data tests. It creates a fresh `build/data/eurovision_features.xlsx`.
To use it in a model notebook, set `DATA_PATH` to that file. The supplied workbook
is kept intact. The optional download mode and source limitations are documented
in notebook 01.

### Check the package and rebuild report figures

```bash
python scripts/verify_package.py
python report/build_report_assets.py
python report/build_extended_assets.py
```

The first command needs only Python's standard library. For LaTeX, open
`report/eurovision_report.tex` with the accompanying `tables/` and `figures/` folders.
The report includes original notebook PNGs where numerical exports were unavailable.

## References

Blangiardo & Baio (2014), *Evidence of bias in the Eurovision song contest:
Modelling the votes using Bayesian hierarchical models*, motivated the use of
hierarchical voting effects. [Open manuscript](https://arxiv.org/abs/1308.6312).
Audio and lyric features are from Adamska & Reiss (2025),
[Eurovision Song Science](https://doi.org/10.5334/tismir.214).
Full source URLs and retrieval records are preserved in the data manifests.
