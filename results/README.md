# Saved results

`task_a/`, `task_b/`, `task_c/` correspond to the three numbered model notebooks.

- `market/`: original CSV exports, diagnostics and plots for the runs with odds.
  Annual metrics and individual prediction exports allow scores to be recomputed.
- `matched_core/`: completed supplied notebooks without odds and extracted summary
  tables. Aggregate values retain four decimal places; the displayed individual
  probabilities retain 0.1 percentage point precision. Full per-year no-odds
  probability exports were not supplied. Do not recompute exact losses from these
  rounded tables or infer precision from their CSV formatting.
- `generated/`: new fits and EDA exports; ignored by Git so archived results remain
  separate from reruns.

The completed notebooks preserve saved outputs. Their input/output paths and
metadata have been adapted for this folder; model definitions and saved numerical
outputs were not changed. The runnable notebooks under `notebooks/` start without
model outputs and default to the market experiment.

Large posterior arrays and duplicate ZIP exports are omitted. Running the model
notebooks recreates posterior draws. Model fitting was not repeated while
assembling this repository; the data reconstruction was checked separately.
