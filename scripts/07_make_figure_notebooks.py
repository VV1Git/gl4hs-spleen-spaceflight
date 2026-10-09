#!/usr/bin/env python3
"""
Turn the two figure scripts into Colab-ready notebooks, so that every figure in
the deck has a notebook that produces it, in the same way notebooks 6 and 7
produce every number.

  NB8  data figures   (from 03_figures_data.py)  - reads results/ from NB6+NB7
  NB9  schematics     (from 04_schematics.py)    - no data dependency
"""
import json
import os

OUT = "notebooks"
os.makedirs(OUT, exist_ok=True)


def md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": src.rstrip("\n").split("\n")}


def code(src):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
            "source": src.rstrip("\n").split("\n")}


def write(name, cells):
    nb = {"cells": cells,
          "metadata": {"colab": {"provenance": [], "toc_visible": True},
                       "kernelspec": {"display_name": "Python 3", "name": "python3"},
                       "language_info": {"name": "python"}},
          "nbformat": 4, "nbformat_minor": 0}
    for c in nb["cells"]:
        c["source"] = [l + "\n" for l in c["source"][:-1]] + [c["source"][-1]]
    p = f"{OUT}/{name}"
    json.dump(nb, open(p, "w"), indent=1)
    print("  wrote", p, f"({len(cells)} cells)")


def split(path, marker_prefix):
    """Split a script into (preamble, [(header, body), ...]) at section markers."""
    lines = open(path).read().split("\n")
    idx = [i for i, l in enumerate(lines) if l.startswith(marker_prefix)]
    pre = "\n".join(lines[:idx[0]])
    blocks = []
    for n, i in enumerate(idx):
        end = idx[n + 1] if n + 1 < len(idx) else len(lines)
        blocks.append((lines[i].strip("# =").strip(), "\n".join(lines[i + 1:end])))
    return pre, blocks


SHOW = """
# show the figure inline as well as writing the PNG
from IPython.display import Image, display
display(Image(filename=f"{FIG}/%s.png", width=900))
"""

# ================================================================ NB8 =======
pre, blocks = split("scripts/03_figures_data.py", "# ====")

c = []
c.append(md("""# NOTEBOOK 8: Presentation figures from the analysis results — OSD-420

**The Spleen Machine (OSD-420-3)** · Kireeti, Pranav, Aryan, Vedant · Interlake High School

Every data figure in the capstone deck is built here. Each one is drawn at the size it is
displayed at on the slide, so the point sizes you set are the point sizes the audience sees.
Scaling a figure down inside PowerPoint is what turns 13pt axis labels into 6pt ones.

## What this notebook needs

It reads the CSV files written by **Notebook 6** (differential expression) and **Notebook 7**
(pathways). Run those first, or place their `results/` folder next to this notebook.

| File | Written by | Used for |
|---|---|---|
| `results/deseq2_full_results.csv` | NB6 | volcano, modules, heme, contamination |
| `results/normalized_counts.csv` | NB6 | QC PCA |
| `results/vst_counts.csv` | NB6 | QC PCA |
| `results/sample_metadata.csv` | NB6 | group labels |
| `results/pca.json` | NB6 | variance explained, depth correlation |
| `results/contamination_scores.csv` | NB6 | contamination QC panel |
| `results/pathways/gsea_significant.csv` | NB7 | GSEA bar chart |
| `results/pathways/gsea_leading_edge_genes.csv` | NB7 | heme leading edge |

## On the colour palette

Three categorical hues carry the three modules: teal-green `#14876b`, terracotta `#a34517`,
plum `#7c42ab`. They were checked with a colourblindness validator against a white surface —
worst-pair separation is ΔE 9.8 under deuteranopia and 22.2 under normal vision. Every
colour-coded series is also directly labelled, so nothing in the deck depends on colour alone.
That is a 508 accessibility requirement, not a preference."""))

c.append(md("""## Setup

`Agg` is the non-interactive matplotlib backend, which is what you want when the job is to write
PNG files rather than to draw on screen. Each figure is displayed inline afterwards so you can
check it here."""))
c.append(code(pre))

c.append(md("""## Check the inputs are present

If this cell fails, run Notebook 6 and Notebook 7 first."""))
c.append(code('''import os

need = [
    "results/deseq2_full_results.csv",
    "results/normalized_counts.csv",
    "results/vst_counts.csv",
    "results/sample_metadata.csv",
    "results/pca.json",
    "results/contamination_scores.csv",
    "results/pathways/gsea_significant.csv",
    "results/pathways/gsea_leading_edge_genes.csv",
]
missing = [f for f in need if not os.path.exists(f)]
if missing:
    raise FileNotFoundError(
        "Run Notebook 6 and Notebook 7 first. Missing:\\n  " + "\\n  ".join(missing))
print(f"All {len(need)} input files present.")'''))

NOTES8 = {
    "FIGURE: QC": """## Figure 3 — quality control before testing

Two panels, and the left one is the argument.

**Left:** PC1 of the raw counts against library size. Spearman ρ = +0.988. Before touching any
biology, this says the largest axis of variation in the raw data is how deeply each sample was
sequenced. Any filter applied to raw counts inherits that, which is exactly how the old
coefficient-of-variation filter became a sequencing-depth filter in disguise.

**Right:** the same samples after variance-stabilising transformation. Flight and ground do not
separate (p = 0.38). Showing this rather than hiding it sets the expectation for the rest of the
talk: the effect is coordinated and subtle, not dramatic.""",
    "FIGURE: VOLCANO": """## Figure 4 — differential expression

146 genes at adjusted p < 0.05, 83 up and 63 down. No fold-change gate is applied, because at
|log₂FC| > 2 this dataset yields zero genes — the real signal is many genes moving moderately in
the same direction.

Gpx3 sits alone at the top: log₂FC +0.91, adjusted p = 7.0 × 10⁻¹⁶, mean count 1,993. The fold
change is modest and the p-value is extreme because every flight sample is higher than every
control sample. That is what consistency buys you.""",
    "FIGURE: THREE LINES (MOD)": """## Figure 5 — three coordinated modules

Six representative genes per module, with 95% confidence intervals from DESeq2's standard errors.
Filled dots are individually significant; open dots are not.

The p-value on each module is a **rank-sum test of that module's fold changes against all 10,546
tested genes**. That is the question worth asking — is this group of genes unusual for this
dataset — rather than whether three genes happen to agree with each other, which they would by
chance often enough.""",
    "FIGURE: GSEA / PATHWAYS": """## Figure 6 — pathway enrichment

Gene set enrichment across GO Biological Process, MSigDB Hallmark and Reactome, with phenotype
permutation. Every term shown passes both FDR q < 0.25 and family-wise error rate < 0.25.

This slide matters because it reaches the same three modules by a completely different statistical
route — no per-gene thresholds at all, just the ranked list scored against whole gene sets. It
also surfaces a fourth signal nobody went looking for: proliferation is down.

The axon guidance term always draws a question. In a non-neural tissue that leading edge is
semaphorins, neuropilins and plexins, whose job in spleen is patterning blood vessels. Check it
gene by gene before you present it.""",
    "FIGURE: HEME LEADING EDGE": """## Heme metabolism leading edge

The genes driving the heme result, with their real fold changes. This is the check the course
insists on: a pathway is only as good as the fold changes of the genes inside it, and a term with
an attractive name whose members did not move is not a result.

Here the leading edge is the entire heme biosynthesis route (Alas2, Urod, Cpox, Fech, Hmbs) plus
the red-cell membrane skeleton (Gypa, Ahsp, Slc4a1, Trim10). A programme, not a gene.""",
    "FIGURE: CONTAMINATION QC": """## Contamination screen

The spleen sits against the liver and the pancreas, and a trace of neighbouring tissue comes
across on the blade. This panel scores an explicit liver marker set and pancreas marker set in
every sample.

71 transcripts were removed before testing. This is what produced the old run's "hepatic
lipidosis" result: four of its ten reported genes (Alb, Apoa2, Serpina3k, Mup3) are
liver-secreted plasma proteins whose median count in spleen is about zero.

Worth noting for questions — the pancreatic transcripts hit tens of thousands of counts in three
samples yet produce no differentially expressed genes, because they happen to be balanced across
groups. The liver panel is the same phenomenon but group-imbalanced, which is precisely how a
false result gets made.""",
}

for header, bodysrc in blocks:
    key = header.strip()
    note = NOTES8.get(key)
    if note:
        c.append(md(note))
    else:
        c.append(md("## " + key.title()))
    c.append(code(bodysrc))

c.append(md("""## All figures written

Each PNG is 300 dpi and sized for its slide. The deck places them without rescaling."""))
c.append(code('''import glob
from IPython.display import Image, display
for f in sorted(glob.glob(f"{FIG}/*.png")):
    print(f"{f}   ({os.path.getsize(f)/1024:.0f} KB)")
    display(Image(filename=f, width=900))'''))

write("NB8_figures_from_results.ipynb", c)

# ================================================================ NB9 =======
pre9, blocks9 = split("scripts/04_schematics.py", "# ====")

c = []
c.append(md("""# NOTEBOOK 9: Schematic figures — OSD-420

**The Spleen Machine (OSD-420-3)** · Kireeti, Pranav, Aryan, Vedant · Interlake High School

The five drawn figures in the deck: the mission and study design, the analysis pipeline, the
biological model, the experimental design for the three aims, and the expected results.

These are hand-authored SVG rendered to PNG with `cairosvg`, in the visual language BioRender
uses — one surface colour, one ink pair, flat cards with thin strokes, generous whitespace, no
gradients or drop shadows. Building them as SVG rather than in a drawing tool means every figure
is reproducible from this notebook, and a colour or a number can be changed in one place.

**Attribution.** All five are our own drawings, so each carries the line *"Image produced by
The Spleen Machine for the 2026 Capstone Showcase"* on the slide. If you swap any of these for a
BioRender export, that figure needs BioRender's own attribution line instead, and a figure taken
from a journal needs its Creative Commons or permission wording.

This notebook has **no data dependency** — it does not read `results/`, so it runs on its own."""))

c.append(md("""## Setup

`cairosvg` is not preinstalled in Colab."""))
c.append(code("!pip install -q cairosvg"))
c.append(code(pre9))

NOTES9 = {
    "1. MISSION & DESIGN": """## Figure 1 — mission and study design

Rodent Research 9, twenty male C57BL/6J mice, SpaceX CRS-12, 33 days on the ISS.

The bottom right card is the one that matters. Hurricane Irma cancelled the original
ground-control run, so it was redone nine months later with different mice. Group, cohort,
dissection session and library batch are therefore the same variable, and no statistical
adjustment separates them. Putting that on the slide rather than in a footnote is a deliberate
choice — most teams will present a flight-versus-ground comparison without saying it.""",
    "2. PIPELINE": """## Figure 2 — analysis pipeline

Seven steps from 57,278 raw STAR counts to 25 enriched pathways, with the gene count at each
step so the audience can follow where everything went.

The ERCC removal step deserves a sentence when you present it: Mix 1 went to every flight sample
and Mix 2 to every ground sample, so spike-in identity **is** group. Leaving them in would corrupt
the size factors in a group-dependent way.""",
    "3. THE MODEL": """## Figure 7 — the biological model

Ground control on the left with organised white-pulp zones and active erythropoiesis, the three
measured signals in the middle, and the flight state on the right: stroma-dominated, zones
blurred.

This is the figure the hypothesis is read against, so the three coloured cards use the same three
hues as the data figures. A viewer who learned "teal is stromal" on slide 5 does not have to
relearn it here.""",
    "4. AIMS / DESIGN": """## Figure 8 — experimental design

The shared ground analogue across the top, then one card per aim.

Note the wording: **ground-based spaceflight analog**, not "simulated spaceflight". True
spaceflight conditions cannot be reproduced on Earth, and the current convention is to call these
analog studies. The model is 28 days of hindlimb unloading against ambulatory controls housed and
handled identically; the flow cytometry and colony assays are measurements, not the model.

The perfusion step is what makes Aim 1 answerable at all — without it you are measuring trapped
blood rather than blood production.""",
    "5. EXPECTED RESULTS": """## Expected results

Held in reserve for questions rather than placed on a slide. Useful if a judge asks what a
positive result would actually look like.""",
}

for header, bodysrc in blocks9:
    key = header.strip()
    note = NOTES9.get(key)
    c.append(md(note if note else "## " + key.title()))
    c.append(code(bodysrc))

c.append(md("""## All schematics written

Both the SVG source and the 300 dpi PNG are kept. Edit the SVG-generating code above rather than
the SVG files, so the notebook stays the single source of truth."""))
c.append(code('''import glob, os
from IPython.display import Image, display
for f in sorted(glob.glob(f"{FIG}/fig_*.png")):
    if os.path.exists(f.replace(".png", ".svg")):
        print(f)
        display(Image(filename=f, width=900))'''))

write("NB9_schematic_figures.ipynb", c)
print("\nFigure notebooks done.")
