EUROVISION REPORT — OVERLEAF PACKAGE

Upload the complete ZIP to Overleaf. Set eurovision_report.tex as the main document and use pdfLaTeX (or XeLaTeX).

eurovision_report.tex: manuscript.
tables/: editable LaTeX tables.
figures/: vector PDFs used in the manuscript and their PNG previews; three original no-odds annual-score PNGs are embedded directly.
evidence/: numerical source snapshots and provenance.
build_report_assets.py: regenerates the main result tables, market-increment plot and coefficient plot.
build_extended_assets.py: regenerates descriptive tables, EDA figures, the additional evaluation tables, calibration, and the 2025 forecast comparisons.
Both scripts use Python 3.10+, numpy, pandas and matplotlib. Run them in that order. Neither script fits models. The original annual-score PNGs remain unchanged.
FIGURE_SOURCE_GUIDE.txt: sources and analytical purpose of each included figure/table group; reasons for not duplicating other notebook plots.

Without-odds aggregate results were extracted from four-decimal notebook displays. Individual forecast probabilities were extracted from HTML tables displayed to 0.1 percentage point. Losses are taken from the aggregate outputs, not recomputed from rounded probabilities. No model fitting was rerun for this report.

Source notebooks: Untitled26 (1).ipynb; forecast_A_models (1).ipynb; forecast_B_models (1).ipynb; forecast_C_models (3)(1).ipynb (identical cells to forecast_C_models (3).ipynb).

Course submission requirements specify an .ipynb with explanatory text and reproducible calculations. This package supplies the requested written report, not the later submission notebook/repository.
