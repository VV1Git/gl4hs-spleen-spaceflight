#!/usr/bin/env python3
"""
Turn the corrected pipeline into two Colab-ready notebooks that mirror the
structure of the GL4HS capstone notebooks 6 and 7, with a markdown cell above
every change explaining what was wrong and why the new version is right.
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


def write(name, cells, title):
    nb = {"cells": cells,
          "metadata": {"colab": {"provenance": [], "toc_visible": True},
                       "kernelspec": {"display_name": "Python 3", "name": "python3"},
                       "language_info": {"name": "python"}},
          "nbformat": 4, "nbformat_minor": 0}
    # keep source lines newline-terminated the way nbformat expects
    for c in nb["cells"]:
        c["source"] = [l + "\n" for l in c["source"][:-1]] + [c["source"][-1]]
    p = f"{OUT}/{name}"
    json.dump(nb, open(p, "w"), indent=1)
    print("  wrote", p, f"({len(cells)} cells)")


# ============================================================ NOTEBOOK 6 ====
c6 = []
c6.append(md("""# NOTEBOOK 6 (CORRECTED): Differential gene expression analysis — OSD-420

**The Spleen Machine (OSD-420-3)** · Kireeti, Pranav, Aryan, Vedant

This replaces `420-parameterized_performing_dgea_capstone`. It runs top to bottom in
Colab with no Google Drive mount required — everything is downloaded from NASA OSDR.

---

## What was wrong with the previous run, and what changed

| # | Previous version | Why it was wrong | This version |
|---|---|---|---|
| 1 | `CV_THRESH = 1.0`, applied before DESeq2 | A coefficient-of-variation filter on **raw counts** is a low-expression filter in disguise: correlation between log₁₀ mean count and CV is **−0.918**. It deleted 78% of expressed genes, including **Gpx3**, the strongest signal in the dataset. | **Removed entirely.** |
| 2 | `drop_lowcount(threshold=50)` — row sum across all 20 samples | One deep or one contaminated library can carry a gene through on its own. | **CPM > 1 in at least 10 samples** — the gene has to be present across a whole group. |
| 3 | No contamination screen | Four of the ten reported genes (Alb, Apoa2, Serpina3k, Mup3) are liver-secreted plasma proteins with a median count of ~0 in spleen. They drove the "hepatic lipidosis" result. | **Explicit liver + pancreas panel, scored per sample and excluded** before testing. |
| 4 | `adj p < 0.05` **and** `abs(log2FC) > 2` used to *select* genes | At \\|log₂FC\\| > 2 this dataset yields **0 genes** on the full gene set. Combining that gate with the CV filter selects for transcripts near zero in one group, where log ratios explode. | Selection on **adjusted p only**; fold change reported as an annotation, with a full threshold-sensitivity table. |
| 5 | PCA on raw counts, PC1 = 90.4% reported without comment | That PC1 is library size (Spearman ρ = **+0.99**), not biology. | PCA on **both** raw and normalised counts, with the depth correlation printed. |
| 6 | Comment said contrast was "ground control vs space flight" | The code was right, the documentation was inverted — anyone reading it flips the sign of every gene. | Direction stated and asserted: **positive log₂FC = higher in spaceflight**. |
| 7 | `counts` and `factors` aligned by row position | Correct only by luck, because both orderings happened to put all flight samples first. | Aligned by **sample name**, with an assertion. |
| 8 | Number of genes with a non-NaN adjusted p never printed | The multiple-testing denominator was ~442, unreported. | Printed explicitly (**10,546**). |

**Result:** 22 of 23 reference genes recovered, versus 1 of 18 before."""))

c6.append(code("""# ---- environment -----------------------------------------------------------
!pip install -q pydeseq2==0.5.4 gseapy==1.3.1

import datetime, os, json
import numpy as np, pandas as pd
from scipy import stats

START = datetime.datetime.now()
print("notebook start:", START.strftime("%Y-%m-%d %H:%M:%S"))

OSD = "420"
DATA, OUT = "data", "results"
os.makedirs(DATA, exist_ok=True); os.makedirs(OUT, exist_ok=True)"""))

c6.append(md("""## 1. Parameters

Everything tunable lives here. Note what is **not** here: there is no `CV_THRESH`
and no fold-change threshold used for gene selection."""))

c6.append(code("""ALPHA     = 0.05   # adjusted p-value threshold
CPM_MIN   = 1.0    # a gene must exceed this CPM ...
CPM_NSAMP = 10     # ... in at least this many samples (= one full group)

# If you change anything here you MUST re-run Notebook 7 as well.
# Parameter drift between the two notebooks is a named course mistake."""))

c6.append(md("""## 2. Download the data

Straight from the NASA Open Science Data Repository, so the notebook is
reproducible by anyone without a Drive folder."""))

c6.append(code("""BASE = f"https://osdr.nasa.gov/geode-py/ws/studies/OSD-{OSD}/download?source=datamanager&file="
FILES = {
    "counts.csv":      f"GLDS-{OSD}_rna_seq_STAR_Unnormalized_Counts_GLbulkRNAseq.csv",
    "genelab_dge.csv": f"GLDS-{OSD}_rna_seq_differential_expression_GLbulkRNAseq.csv",
    "isa.zip":         f"GLDS-{OSD}_metadata_GLDS-{OSD}-ISA.zip",
}
for local, remote in FILES.items():
    if not os.path.exists(f"{DATA}/{local}"):
        !curl -sSL -o {DATA}/{local} "{BASE}{remote}"
!unzip -o -q {DATA}/isa.zip -d {DATA}/isa
print(os.listdir(DATA))"""))

c6.append(code("""expr = pd.read_csv(f"{DATA}/counts.csv", index_col=0)
expr.index.name = "ENSEMBL"
FLT = [c for c in expr.columns if "_FLT_" in c]
GC  = [c for c in expr.columns if "_GC_"  in c]
assert len(FLT) == 10 and len(GC) == 10, "expected 10 flight and 10 ground samples"
print(f"raw counts: {expr.shape[0]:,} genes x {expr.shape[1]} samples")
print(f"Space Flight n={len(FLT)}   Ground Control n={len(GC)}")
expr.head()"""))

c6.append(md("""## 3. Remove the ERCC spike-ins

This matters more here than in most datasets. ERCC consumes **19.8–39.7%** of assigned
counts, and **Mix 1 went to every flight sample while Mix 2 went to every ground sample** —
so spike-in identity is perfectly confounded with experimental group. Leaving them in
would corrupt DESeq2's size factors in a group-dependent way."""))

c6.append(code("""n0 = len(expr)
expr = expr[~expr.index.str.startswith("ERCC-")]
print(f"dropped {n0 - len(expr)} ERCC records -> {len(expr):,} genes")"""))

c6.append(md("""## 4. Gene symbols

Taken from GeneLab's own annotation table rather than a pyensembl download, so the
symbols match the release the counts were generated against. Genes with no symbol keep
their Ensembl ID rather than being silently dropped."""))

c6.append(code("""ann = (pd.read_csv(f"{DATA}/genelab_dge.csv", usecols=["ENSEMBL", "SYMBOL", "GENENAME"])
         .drop_duplicates("ENSEMBL").set_index("ENSEMBL"))
sym = ann["SYMBOL"].reindex(expr.index)
sym = sym.fillna(pd.Series(expr.index, index=expr.index))
print(f"{ann['SYMBOL'].reindex(expr.index).notna().sum():,} genes mapped to a symbol")"""))

c6.append(md("""## 5. Contamination screen — the step the old pipeline was missing

The spleen sits next to the liver, the pancreas and the stomach. Dissection carries a
trace of neighbouring tissue across, and because the two groups were dissected **nine
months apart by possibly different hands**, that carryover is not balanced.

Pancreatic transcripts are the built-in control: they appear at up to ~7,800 ppm in single
samples, but because they happen to be balanced across groups they produce zero DEGs. The
liver panel is the same phenomenon, group-imbalanced — which is exactly how "hepatic
lipidosis" got into the previous result.

We score both panels per sample, plot them, and **exclude them from all testing**."""))

c6.append(code("""LIVER = ["Alb","Apoa1","Apoa2","Apob","Apoc1","Apoc3","Apoc4","Apoh","Apom","Ttr",
         "Fga","Fgb","Fgg","Kng1","Kng2","Ahsg","Orm1","Orm2","Serpina1a","Serpina1b",
         "Serpina1c","Serpina3k","Trf","Hp","Vtn","Ambp","Tf","F2","Cps1","Hpx",
         "Itih1","Itih2","Itih3","Itih4"]
LIVER += [s for s in sym.unique() if isinstance(s, str) and s.startswith("Mup")]
PANCREAS = ["Amy2a1","Amy2a2","Amy2a3","Amy2a4","Amy2a5","Amy2b","Amy1","Cela1","Cela2a",
            "Cela3b","Ctrb1","Ctrl","Pnlip","Pnliprp1","Prss1","Prss2","Try4","Try5",
            "Cpa1","Cpa2","Cpb1","Clps","Cel","Sycn","Pdia2","Reg1","Reg2","Reg3b","Zg16"]

lib  = expr.sum(axis=0)
cpm  = expr / lib * 1e6
liver_idx = sym[sym.isin(LIVER)].index
panc_idx  = sym[sym.isin(PANCREAS)].index
liver = cpm.loc[liver_idx].sum(axis=0)     # parts per million
panc  = cpm.loc[panc_idx].sum(axis=0)

print(f"liver panel    {len(liver_idx):>3} genes | flight median {liver[FLT].median():8.1f} ppm"
      f" | ground median {liver[GC].median():8.1f} ppm"
      f" | Mann-Whitney p = {stats.mannwhitneyu(liver[FLT], liver[GC]).pvalue:.3f}")
print(f"pancreas panel {len(panc_idx):>3} genes | flight median {panc[FLT].median():8.1f} ppm"
      f" | ground median {panc[GC].median():8.1f} ppm"
      f" | Mann-Whitney p = {stats.mannwhitneyu(panc[FLT], panc[GC]).pvalue:.3f}")

contam = liver_idx.union(panc_idx)
n0 = len(expr); expr = expr.drop(index=contam)
print(f"\\nexcluded {n0 - len(expr)} carryover transcripts -> {len(expr):,} genes")"""))

c6.append(code("""import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(10, 3.4))
x = np.arange(20)
order = FLT + GC
cols  = ["#2a78d6"] * 10 + ["#e34948"] * 10
ax.bar(x - 0.2, liver.reindex(order), width=0.4, color=cols, label="liver panel")
ax.bar(x + 0.2, panc.reindex(order),  width=0.4, color=cols, alpha=0.45, hatch="///",
       label="pancreas panel")
ax.set_yscale("log"); ax.set_xticks(x)
ax.set_xticklabels([s.replace("RR9_SPL_", "") for s in order], rotation=60, ha="right", fontsize=8)
ax.set_ylabel("contaminating transcripts (ppm)")
ax.set_title("Dissection carryover, per sample  (blue = flight, red = ground)")
ax.legend(); plt.tight_layout(); plt.show()"""))

c6.append(md("""## 6. Expression prefilter

`CPM > 1 in at least 10 samples`. Ten is the size of one group, so a gene qualifies if it
is genuinely present in flight **or** in ground — which is what we want, since a gene that
is off in one group and on in the other is real biology, not noise.

Compare: the previous pipeline reached DESeq2 with **4,080** genes, of which only ~442 ever
received an adjusted p-value."""))

c6.append(code("""cpm  = expr / expr.sum(axis=0) * 1e6
keep = (cpm > CPM_MIN).sum(axis=1) >= CPM_NSAMP
n0 = len(expr); expr = expr[keep]
print(f"prefilter removed {n0 - len(expr):,} genes -> {len(expr):,} genes into DESeq2")"""))

c6.append(md("""## 7. DESeq2

All 20 animals are male C57BL/6J at one age with one flight duration, so there is no
second factor to model. **Single-factor `~ condition` is the only legitimate design** —
we state that rather than forcing a multi-factor config.

`contrast=("condition", "Space_Flight", "Ground_Control")` means
**positive log₂ fold change = higher in spaceflight**."""))

c6.append(code("""from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds  import DeseqStats

counts = expr.T.astype(int)                       # samples x genes
meta = pd.DataFrame(
    {"condition": ["Space_Flight" if s in FLT else "Ground_Control" for s in counts.index]},
    index=counts.index)
assert list(counts.index) == list(meta.index), "sample order must match by NAME, not position"

dds = DeseqDataSet(counts=counts, metadata=meta, design="~condition", refit_cooks=True, quiet=True)
dds.deseq2()

st  = DeseqStats(dds, contrast=["condition", "Space_Flight", "Ground_Control"], quiet=True)
st.summary()
res = st.results_df.copy()
res["SYMBOL"]   = sym.reindex(res.index).values
res["GENENAME"] = ann["GENENAME"].reindex(res.index).values
res = res.sort_values("padj")

print(f"\\ngenes with a non-NaN adjusted p (the BH denominator): {res['padj'].notna().sum():,}"
      f" of {len(res):,}")"""))

c6.append(md("""## 8. Threshold sensitivity

The single most useful sanity check available, and the one the previous run could not
produce. Notice the last row: **at |log₂FC| > 2 this dataset yields nothing.** Any pipeline
that reports ten genes at that threshold is finding artefacts."""))

c6.append(code("""rows = []
for a, lfc in [(0.05, 0), (0.05, 1), (0.05, 1.5), (0.05, 2), (0.10, 0), (0.01, 0)]:
    m = (res["padj"] < a) & (res["log2FoldChange"].abs() > lfc)
    rows.append({"adj_p": a, "min_|log2FC|": lfc, "n": int(m.sum()),
                 "up": int((m & (res.log2FoldChange > 0)).sum()),
                 "down": int((m & (res.log2FoldChange < 0)).sum())})
sens = pd.DataFrame(rows); display(sens)

sig = res[res["padj"] < ALPHA].copy()
print(f"HEADLINE: {len(sig)} genes at adjusted p < {ALPHA} "
      f"({(sig.log2FoldChange > 0).sum()} up in flight, {(sig.log2FoldChange < 0).sum()} down)")
res.to_csv(f"{OUT}/deseq2_full_results.csv"); sig.to_csv(f"{OUT}/deseq2_significant.csv")
sig.head(20)[["SYMBOL", "baseMean", "log2FoldChange", "padj"]]"""))

c6.append(md("""## 9. Cross-check against GeneLab's delivered analysis

Different filtering, same biology. If these two disagreed in *direction*, something would
be wrong with our pipeline."""))

c6.append(code("""gl = (pd.read_csv(f"{DATA}/genelab_dge.csv",
                  usecols=["ENSEMBL", "Log2fc_(Space Flight)v(Ground Control)",
                           "Adj.p.value_(Space Flight)v(Ground Control)"])
        .rename(columns={"Log2fc_(Space Flight)v(Ground Control)": "gl_log2FC",
                         "Adj.p.value_(Space Flight)v(Ground Control)": "gl_padj"})
        .drop_duplicates("ENSEMBL").set_index("ENSEMBL"))
gl_sig = gl[gl.gl_padj < 0.05]
ours, theirs = set(sig.index), set(gl_sig.index)
j = res.join(gl, how="inner").dropna(subset=["log2FoldChange", "gl_log2FC"])
print(f"GeneLab significant: {len(gl_sig)}   ours: {len(ours)}   overlap: {len(ours & theirs)}")
print(f"log2FC correlation across {len(j):,} shared genes: r = {np.corrcoef(j.log2FoldChange, j.gl_log2FC)[0,1]:.4f}")"""))

c6.append(md("""## 10. Did we recover the genes the old pipeline lost?

The previous run recovered **1 of 18**. Every gene below is at a healthy expression level,
so none of these is a sparse-count artefact."""))

c6.append(code("""REF = ["Gpx3","Sparcl1","Pdgfra","Cxcl12","Apoe","Maf","Aebp1","Cldn5","Kdr","Wt1",
       "Ank1","Trim10","Gypa","Hmbs",
       "Rgs13","Fcer2a","Ccr7","Madcam1","Isg15","Ifi27l2a","Rsad2","Trim30a","Ccna2"]
rec = res[res.SYMBOL.isin(REF)][["SYMBOL","baseMean","log2FoldChange","padj"]].copy()
rec["significant"] = rec.padj < ALPHA
display(rec.sort_values("padj"))
print(f"recovered {int(rec.significant.sum())} of {len(REF)} reference genes")"""))

c6.append(md("""## 11. Module-level tests — the three lines of evidence

The course requires **three corroborating lines of evidence**. A line of evidence is much
stronger if the whole module moves, not just one gene, so we test each module two ways:

* **self-contained** — Wilcoxon signed-rank of the module's fold changes against zero
* **competitive** — Mann-Whitney rank-sum of the module against all other tested genes

The competitive test is the one that answers "is this module unusual *for this dataset*"."""))

c6.append(code("""MODULES = {
 "Stromal / perivascular (UP)":  ["Gpx3","Sparcl1","Pdgfra","Cxcl12","Apoe","Maf","Aebp1","Cldn5","Kdr","Wt1"],
 "Erythroid / heme (DOWN)":      ["Ank1","Gypa","Trim10","Hmbs","Alas2","Slc4a1","Epb42","Klf1","Tspo2","Hemgn"],
 "Lymphoid organisation (DOWN)": ["Rgs13","Ccr7","Madcam1","Fcer2a","Cxcr5","Cr2","Ccl19","Ccl21a"],
 "Type I interferon (DOWN)":     ["Isg15","Ifi27l2a","Rsad2","Trim30a","Ifit1","Ifit3","Oasl2","Irf7","Stat1","Bst2"],
}
tested = res[res.padj.notna()]
out = []
for name, genes in MODULES.items():
    sub = tested[tested.SYMBOL.isin(genes)]
    if len(sub) < 3: continue
    out.append({"module": name, "n": len(sub), "n_significant": int((sub.padj < ALPHA).sum()),
                "median_log2FC": round(float(sub.log2FoldChange.median()), 3),
                "signed_rank_p": stats.wilcoxon(sub.log2FoldChange).pvalue,
                "rank_sum_p": stats.mannwhitneyu(sub.log2FoldChange, tested.log2FoldChange).pvalue,
                "genes": "; ".join(sub.SYMBOL)})
mods = pd.DataFrame(out); mods.to_csv(f"{OUT}/module_statistics.csv", index=False)
display(mods[["module","n","n_significant","median_log2FC","signed_rank_p","rank_sum_p"]])"""))

c6.append(md("""## 12. PCA — on raw counts *and* on normalised counts

Run it both ways and say what you see. On raw counts PC1 is 98% of the variance and
correlates with library size at ρ ≈ 0.99 — it is sequencing depth. After normalisation the
groups do not separate (p ≈ 0.4).

That second result is a limitation, not a failure, and it belongs on the slide."""))

c6.append(code("""from sklearn.decomposition import PCA
norm = pd.DataFrame(dds.layers["normed_counts"], index=counts.index, columns=counts.columns)
vst  = np.log2(norm + 1)
grp  = np.array([1 if s in FLT else 0 for s in counts.index])

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for ax, (tag, mat) in zip(axes, [("raw counts", counts.astype(float)), ("log2 normalised", vst)]):
    X = mat.values - mat.values.mean(axis=0)
    p = PCA(n_components=2, svd_solver="full", random_state=0)   # 'full' = deterministic
    Y = p.fit_transform(X)
    rho = stats.spearmanr(Y[:, 0], counts.sum(axis=1).values)
    pv  = stats.mannwhitneyu(Y[grp == 1, 0], Y[grp == 0, 0]).pvalue
    for m, lab, c in [(grp == 1, "Space Flight", "#2a78d6"), (grp == 0, "Ground Control", "#e34948")]:
        ax.scatter(Y[m, 0], Y[m, 1], s=70, color=c, edgecolor="white", label=lab)
    ax.set_title(f"{tag}\\nPC1 {p.explained_variance_ratio_[0]*100:.1f}%  ·  "
                 f"PC1 vs depth rho={rho.statistic:+.2f}  ·  groups p={pv:.2f}", fontsize=10)
    ax.set_xlabel("PC1"); ax.set_ylabel("PC2"); ax.legend(fontsize=8)
plt.tight_layout(); plt.show()
norm.T.to_csv(f"{OUT}/normalized_counts.csv"); meta.to_csv(f"{OUT}/sample_metadata.csv")"""))

c6.append(md("""## 13. Volcano plot

Interpret it out loud when you present it: the cloud is asymmetric, the significant genes
are moderate in magnitude, and the named genes fall into three groups."""))

c6.append(code("""t = res[res.padj.notna()]
x, y = t.log2FoldChange.values, -np.log10(t.padj.values)
s_ = t.padj.values < ALPHA
fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(x[~s_], y[~s_], s=6, color="#c9c8c3", alpha=.6, lw=0)
ax.scatter(x[s_ & (x > 0)], y[s_ & (x > 0)], s=20, color="#2a78d6", label=f"up in flight (n={(s_&(x>0)).sum()})")
ax.scatter(x[s_ & (x < 0)], y[s_ & (x < 0)], s=20, color="#e34948", label=f"down in flight (n={(s_&(x<0)).sum()})")
ax.axhline(-np.log10(ALPHA), ls="--", color="#8a8985", lw=1)
for g in ["Gpx3","Sparcl1","Maf","Apoe","Cxcl12","Rgs13","Trim10","Gypa","Isg15","Ifi27l2a"]:
    m = np.where(t.SYMBOL.values == g)[0]
    if len(m):
        ax.annotate(g, (x[m[0]], y[m[0]]), (x[m[0]] + .18, y[m[0]] + .25), fontsize=9, fontweight="bold")
ax.set_xlabel("log2 fold change  (Space Flight vs Ground Control)")
ax.set_ylabel("-log10 adjusted p-value"); ax.legend(); plt.tight_layout(); plt.show()"""))

c6.append(md("""## 14. Hand-off to Notebook 7

The background list is the genes **actually tested by DESeq2** (non-NaN adjusted p), not the
prefiltered set — that is the correct universe for over-representation analysis.

Up and down lists are written separately. An asymmetric split is the informative case, and a
merged list cancels direction."""))

c6.append(code("""sig_t = res[(res.padj < ALPHA)].dropna(subset=["SYMBOL"])
open(f"{OUT}/deg_genes.txt", "w").write("\\n".join(sig_t.SYMBOL) + "\\n")
open(f"{OUT}/deg_up.txt",   "w").write("\\n".join(sig_t[sig_t.log2FoldChange > 0].SYMBOL) + "\\n")
open(f"{OUT}/deg_down.txt", "w").write("\\n".join(sig_t[sig_t.log2FoldChange < 0].SYMBOL) + "\\n")
open(f"{OUT}/background_genes.txt", "w").write(
    "\\n".join(res[res.padj.notna()].SYMBOL.dropna().unique()) + "\\n")
print(f"DEGs {len(sig_t)}  (up {(sig_t.log2FoldChange>0).sum()}, down {(sig_t.log2FoldChange<0).sum()})")
print(f"background {res.padj.notna().sum():,} genes")
print("elapsed:", datetime.datetime.now() - START)"""))

write("NB6_CORRECTED_OSD420_dgea.ipynb", c6, "NB6")

# ============================================================ NOTEBOOK 7 ====
c7 = []
c7.append(md("""# NOTEBOOK 7 (CORRECTED): Pathway analysis — GSEA and ORA — OSD-420

**The Spleen Machine (OSD-420-3)**

Run **Notebook 6 (corrected) first** — this notebook reads its outputs from `results/`.
If you change a parameter in Notebook 6 you must re-run this notebook too; parameter drift
between the two is a named course mistake.

---

## What was wrong with the previous run, and what changed

| # | Previous version | Why it was wrong | This version |
|---|---|---|---|
| 1 | `run_ora()` took a `background_genes` argument and **never passed it to `gp.enrichr`** | Every ORA p-value was computed against Enrichr's whole-genome default (~20,000 genes) instead of the genes actually tested. The markdown claimed the opposite. | `gp.enrichr(..., background=background)` — and the background is the **tested** set. |
| 2 | `permutation_type='gene_set'`, with the notebook's own comment saying to use phenotype at n ≥ 15 | Gene-set permutation destroys gene–gene correlation structure, so any co-regulated block — such as one contaminating tissue — scores as wildly significant. There are 20 samples. | `permutation_type='phenotype'` |
| 3 | GSEA run on **raw** counts | `signal_to_noise` on raw counts conflates expression with library size. | Run on **DESeq2 normalised counts**. |
| 4 | `min_size=5` on GO, gseapy default of 15 on GEO, `max_size` never set | Drift inside one notebook, and 500+ member sets eligible against a 10-gene list. | `min_size=15`, `max_size=300`, the same for every library. |
| 5 | Terms filtered on FWER alone | Terms at FDR q = 0.27 and q = 0.35 were reported as significant. | **FDR q < 0.25 AND FWER < 0.25.** |
| 6 | `display_cols` excluded `Overlap` | Gene-set size and fold enrichment could not be reported at all — both are required by the course. | Overlap, set size, **fold enrichment** and odds ratio all reported. |
| 7 | Six of ten reported GO terms were **single-gene** overlaps, and the gene was APOA2 (a contaminant) | A one-gene overlap is not an enrichment; it is that gene's annotation with a p-value attached. | Terms with fewer than 3 overlapping genes are dropped. |
| 8 | `!cat go_gsea_results.csv` where `geo_` was meant | The GEO results were computed and never looked at. | Every result set is displayed. |
| 9 | `title=terms.iloc[0]` inside a loop over `i` | All eleven heatmaps carried the same title. | `terms.iloc[i]`. |
| 10 | Enrichment tables reported without checking member genes | The lecture calls the download-back-to-your-data loop the single most important procedural step. | Every reported term's member genes are written out with their real log₂FC and adjusted p. |"""))

c7.append(code("""!pip install -q gseapy==1.3.1

import os
import numpy as np, pandas as pd, gseapy as gp
from scipy import stats
import matplotlib.pyplot as plt

OUT = "results"; os.makedirs(f"{OUT}/pathways", exist_ok=True)

ALPHA       = 0.05    # must match Notebook 6
FDR_T       = 0.25
FWER_T      = 0.25
MIN_SET     = 15      # smallest gene set worth testing
MAX_SET     = 300     # largest -- avoids 500+ member sets against a small list
MIN_OVERLAP = 3       # a term needs at least 3 of your genes to be reportable
SEED        = 7

LIBS = ["GO_Biological_Process_2025", "GO_Cellular_Component_2025",
        "MSigDB_Hallmark_2020", "Reactome_Pathways_2024"]"""))

c7.append(code("""res  = pd.read_csv(f"{OUT}/deseq2_full_results.csv", index_col=0)
norm = pd.read_csv(f"{OUT}/normalized_counts.csv", index_col=0)

tested = res[res.padj.notna()].dropna(subset=["SYMBOL"]).sort_values("baseMean", ascending=False)
tested = tested[~tested.SYMBOL.duplicated()]          # collapse by highest baseMean, not by averaging
background = tested.SYMBOL.tolist()
sig = tested[tested.padj < ALPHA]
up_list, dn_list = sig[sig.log2FoldChange > 0].SYMBOL.tolist(), sig[sig.log2FoldChange < 0].SYMBOL.tolist()
lookup = tested.set_index("SYMBOL")[["log2FoldChange", "padj", "baseMean"]]

print(f"background {len(background):,} genes | significant {len(sig)} "
      f"| UP {len(up_list)} | DOWN {len(dn_list)}")
print("Course guidance: 10-50 genes is the sweet spot, up to ~100. Analyse UP and DOWN separately.")"""))

c7.append(md("""## GSEA

Phenotype permutation, normalised counts, bounded set sizes, seeded so it reproduces."""))

c7.append(code("""expr = norm.copy()
expr.index = res.SYMBOL.reindex(expr.index).values
expr = expr[~pd.isna(expr.index)].groupby(level=0).max()
expr = expr.loc[[g for g in expr.index if g in set(background)]]
cls  = ["Space_Flight" if "_FLT_" in s else "Ground_Control" for s in expr.columns]
print(f"{expr.shape[0]:,} genes x {expr.shape[1]} samples · positive NES = higher in SPACE FLIGHT")

frames = []
for lib in LIBS:
    print("running", lib, "...")
    r = gp.gsea(data=expr, gene_sets=lib, cls=cls,
                permutation_type="phenotype", permutation_num=1000,
                method="signal_to_noise", min_size=MIN_SET, max_size=MAX_SET,
                threads=2, seed=SEED, outdir=None, no_plot=True)
    d = r.res2d.copy(); d["Library"] = lib; frames.append(d)

g = pd.concat(frames, ignore_index=True)
for c in ["NES", "ES", "NOM p-val", "FDR q-val", "FWER p-val"]:
    g[c] = pd.to_numeric(g[c], errors="coerce")
gs = g[(g["FDR q-val"] < FDR_T) & (g["FWER p-val"] < FWER_T)].sort_values("NES", key=abs, ascending=False)
gs.to_csv(f"{OUT}/pathways/gsea_significant.csv", index=False)
print(f"\\n{len(gs)} terms pass FDR q < {FDR_T} AND FWER < {FWER_T} "
      f"({(gs.NES>0).sum()} up in flight, {(gs.NES<0).sum()} down)")
display(gs[["Term","Library","NES","FDR q-val","FWER p-val","Tag %"]].head(25))"""))

c7.append(md("""### The download-back-to-your-data loop

> *"Getting all the data and inputting data into all of these tools and plotting graphs is
> kind of the easy part. The hard part is understanding what you've done and what it means."*

For every surviving term, pull its leading-edge genes back out and look at their **real**
fold changes and expression levels. A pathway whose member genes barely move, or whose
leading edge is made of genes with near-zero counts, is not a pathway you can build on."""))

c7.append(code("""UP = {str(s).upper(): s for s in lookup.index}       # gseapy uppercases symbols
rows = []
for _, r_ in gs.iterrows():
    for gene in str(r_["Lead_genes"]).split(";"):
        k = UP.get(gene.strip().upper())
        if k is not None:
            rows.append({"Term": r_["Term"], "NES": r_["NES"], "FDR_q": r_["FDR q-val"], "gene": k,
                         "log2FC": lookup.loc[k, "log2FoldChange"],
                         "adj_p": lookup.loc[k, "padj"], "baseMean": lookup.loc[k, "baseMean"]})
led = pd.DataFrame(rows); led.to_csv(f"{OUT}/pathways/gsea_leading_edge_genes.csv", index=False)
chk = (led.groupby("Term").agg(n_lead=("gene","size"),
                               median_log2FC=("log2FC","median"),
                               median_baseMean=("baseMean","median"))
          .sort_values("n_lead", ascending=False))
display(chk.head(20))
print("Read this table before you put any term on a slide. Low median_baseMean = suspect.")"""))

c7.append(code("""fig, ax = plt.subplots(figsize=(9, 5))
top = gs.reindex(gs.NES.abs().sort_values(ascending=False).index).head(14).iloc[::-1]
ax.barh(range(len(top)), top.NES,
        color=["#2a78d6" if v > 0 else "#e34948" for v in top.NES])
ax.set_yticks(range(len(top)))
ax.set_yticklabels([t.split(" (GO:")[0][:46] for t in top.Term], fontsize=8)
for i, (n, q) in enumerate(zip(top.NES, top["FDR q-val"])):
    ax.text(n + (0.05 if n > 0 else -0.05), i, f"q={q:.3f}", va="center",
            ha="left" if n > 0 else "right", fontsize=7)
ax.axvline(0, color="#52514e"); ax.set_xlabel("NES  (positive = higher in spaceflight)")
plt.tight_layout(); plt.show()"""))

c7.append(md("""### Leading-edge heatmaps

Note `terms.iloc[i]`, not `terms.iloc[0]` — the previous notebook titled all eleven
heatmaps with the name of the first term."""))

c7.append(code("""from gseapy import heatmap
show = gs.head(4)
for i in range(len(show)):
    term = show.Term.iloc[i]
    genes = [UP[x.strip().upper()] for x in str(show.Lead_genes.iloc[i]).split(";")
             if x.strip().upper() in UP]
    sub = expr.loc[[gene for gene in genes if gene in expr.index]]
    if len(sub) < 2: continue
    heatmap(df=sub, z_score=0, title=term, figsize=(7, max(2, 0.22 * len(sub))))
    plt.show()"""))

c7.append(md("""## Over-representation analysis

Correct background, up and down analysed separately, fold enrichment reported, and any term
resting on fewer than three of your genes discarded."""))

c7.append(code("""# effective set sizes, restricted to the tested background -- this is the size that matters
bgset = set(x.upper() for x in background)
SETSIZE = {}
for lib in LIBS:
    for term, genes in gp.get_library(name=lib, organism="Mouse").items():
        SETSIZE[(lib, term)] = len(bgset & set(x.upper() for x in genes))

frames = []
for tag, lst in [("UP_in_flight", up_list), ("DOWN_in_flight", dn_list)]:
    if len(lst) < 5: continue
    e = gp.enrichr(gene_list=lst, gene_sets=LIBS, organism="mouse",
                   background=background, outdir=None)          # <-- the fixed line
    d = e.results.copy(); d["direction"] = tag
    d["n_overlap"] = d.Genes.apply(lambda g: len([x for x in str(g).split(";") if x.strip()]))
    d["set_size"]  = [SETSIZE.get((gs_, t_), np.nan) for gs_, t_ in zip(d.Gene_set, d.Term)]
    d["Overlap"]   = d.n_overlap.astype(str) + "/" + d.set_size.astype("Int64").astype(str)
    d["fold_enrichment"] = (d.n_overlap / len(lst)) / (d.set_size / len(background))
    frames.append(d)

o = pd.concat(frames, ignore_index=True)
ora = o[(o["Adjusted P-value"] < ALPHA) & (o.n_overlap >= MIN_OVERLAP) &
        (o.set_size.between(MIN_SET, MAX_SET))].sort_values("Adjusted P-value")
ora.to_csv(f"{OUT}/pathways/ora_significant.csv", index=False)
print(f"{len(ora)} terms pass adj p < {ALPHA}, overlap >= {MIN_OVERLAP}, set size {MIN_SET}-{MAX_SET}")
display(ora[["direction","Term","Overlap","fold_enrichment","Odds Ratio","Adjusted P-value","Genes"]].head(25))
print("Fold enrichment below 1 means NEGATIVELY enriched -- it is a ratio, not a log2 value.")"""))

c7.append(code("""rows = []
for _, r_ in ora.iterrows():
    for gene in str(r_["Genes"]).split(";"):
        k = UP.get(gene.strip().upper())
        if k is not None:
            rows.append({"Term": r_["Term"], "direction": r_["direction"], "Overlap": r_["Overlap"],
                         "fold_enrichment": r_["fold_enrichment"], "adj_p_term": r_["Adjusted P-value"],
                         "gene": k, "log2FC": lookup.loc[k, "log2FoldChange"],
                         "adj_p_gene": lookup.loc[k, "padj"], "baseMean": lookup.loc[k, "baseMean"]})
pd.DataFrame(rows).to_csv(f"{OUT}/pathways/ora_member_genes.csv", index=False)
print(f"wrote {len(rows)} gene-in-term rows -- this is your pathway tracking tab for the worksheet")"""))

c7.append(md("""## Tracking table for the DGEA worksheet

The course requires a pathway-analysis tracking tab recording the tool, the exact gene list
used, the term, its statistics, and each hit gene's adjusted p and log₂FC. `ora_member_genes.csv`
and `gsea_leading_edge_genes.csv` are that table — paste them straight in.

**Record which list went into which tool.** Feeding the wrong list gives silently invalid
results, and it is the failure the instructors warn about most."""))

c7.append(code("""summary = pd.DataFrame([
    {"tool": "GSEA (gseapy)", "input": f"all {expr.shape[0]:,} tested genes, ranked by signal-to-noise",
     "libraries": "; ".join(LIBS), "settings": f"phenotype permutation x1000, size {MIN_SET}-{MAX_SET}, seed {SEED}",
     "terms_reported": len(gs), "filter": f"FDR q < {FDR_T} AND FWER < {FWER_T}"},
    {"tool": "Enrichr ORA (gseapy)", "input": f"{len(up_list)} up / {len(dn_list)} down, analysed separately",
     "libraries": "; ".join(LIBS), "settings": f"background = {len(background):,} tested genes",
     "terms_reported": len(ora), "filter": f"adj p < {ALPHA}, overlap >= {MIN_OVERLAP}, size {MIN_SET}-{MAX_SET}"},
])
summary.to_csv(f"{OUT}/pathways/analysis_tracking.csv", index=False)
display(summary)"""))

write("NB7_CORRECTED_OSD420_pathways.ipynb", c7, "NB7")
print("\nDone.")
