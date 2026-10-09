# The four notebooks

Run them in order. Every number and figure in our capstone slides comes out of one of these.
All four were executed start to finish with no errors before delivery, and the outputs
you see saved in them are from that run.

| # | Notebook | Runtime | Needs | Produces |
|---|---|---|---|---|
| 6 | `NB6_CORRECTED_OSD420_dgea.ipynb` | ~45 s | nothing (downloads from NASA OSDR) | `results/*.csv` |
| 7 | `NB7_CORRECTED_OSD420_pathways.ipynb` | ~20 min | NB6's `results/` | `results/pathways/*.csv` |
| 8 | `NB8_figures_from_results.ipynb` | ~30 s | NB6 + NB7 `results/` | six data figures |
| 9 | `NB9_schematic_figures.ipynb` | ~10 s | nothing | five drawn figures |

Notebook 7 is nearly all GSEA permutations. Start it and go do something else.

Notebook 9 has no data dependency, so you can run it on its own if you only want to change a
label or a colour on one of the drawn figures.

## Where each deck figure comes from

| Slide | Figure | Notebook |
|---|---|---|
| 2 | Figure 1, mission and study design | 9 |
| 3 | Figure 2, analysis pipeline | 9 |
| 3 | Figure 3, quality control | 8 |
| 4 | Figure 4, differential expression | 8 |
| 5 | Figure 5, three modules | 8 |
| 6 | Figure 6, pathway enrichment | 8 |
| 7 | Figure 7, the model | 9 |
| 8 | Figure 8, experimental design | 9 |
| — | heme leading edge, contamination screen, expected results | 8, 8, 9 |

The last three are not on slides. They are there for questions.

## Colab

All four run in Colab with no Google Drive mount. Notebook 6 downloads the counts and metadata
from NASA OSDR directly. Notebooks 8 and 9 install what they need in their first cell.

If you run 8 or 9 in a fresh Colab session, upload the `results/` folder first, or run 6 and 7
in the same session so the files are already there.

## If you change the analysis

Change it in Notebook 6 or 7, re-run, then re-run Notebook 8. The figures read the CSVs, so every
number on every slide follows the analysis automatically. The only numbers typed by hand are the
ones written into the slide text and the speaker notes, and those have to be checked by hand.

## The scripts

The scripts live in `scripts/` and are meant to be run from the repository root, for example `python scripts/01_dgea_corrected.py`. `01_dgea_corrected.py` and `02_pathway_corrected.py` are the same pipelines as notebooks 6 and 7,
as plain scripts, if you want to run the analysis outside Colab. `03_figures_data.py` and
`04_schematics.py` are the same for notebooks 8 and 9. `06_make_notebooks.py` and
`07_make_figure_notebooks.py` are what turned the scripts into the notebooks, so the notebooks
can be regenerated rather than hand-edited. `05_build_deck.js` builds the PowerPoint.
