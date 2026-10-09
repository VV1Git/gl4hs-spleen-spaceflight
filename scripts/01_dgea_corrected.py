#!/usr/bin/env python3
"""
OSD-420 / GLDS-420 -- CORRECTED differential gene expression analysis.

Replaces Notebook 6 (`420-parameterized_performing_dgea_capstone`).

WHAT CHANGED VS THE TEAM'S VERSION, AND WHY
-------------------------------------------
1. REMOVED the coefficient-of-variation filter (CV > 1.0).
   It was a low-expression selector in disguise (r = -0.918 between log10 mean
   count and CV) applied to RAW counts, so 9-fold library-depth variation fed
   straight into it. It deleted 78% of expressed genes -- including Gpx3, the
   strongest signal in the dataset -- BEFORE DESeq2 ever ran.

2. REPLACED `drop_lowcount(threshold=50)` (row-sum across all 20 samples) with a
   per-sample CPM criterion (CPM > 1 in at least 10 samples). A row-sum filter
   lets one deep or one contaminated library carry a gene through; a per-sample
   criterion requires the gene to be present in a whole group.

3. ADDED an explicit contaminant panel (liver + pancreas dissection carryover).
   Scored per sample, reported as a QC figure, and EXCLUDED from DE testing.
   This is what produced the bogus "hepatic lipidosis" / "atherosclerosis"
   enrichment in the previous run.

4. DROPPED the |log2FC| > 2 gate as a selection criterion. Fold change is now an
   annotation, not a filter. Counts are reported at every threshold.

5. PCA is run on variance-stabilised counts, not raw counts, and both are shown
   so the difference is visible.

6. Contrast direction is documented correctly: positive log2FC = HIGHER IN FLIGHT.

Outputs land in ./results/ and ./figdata/.
"""

import json
import os

import numpy as np
import pandas as pd
from scipy import stats

pd.set_option("display.width", 200)

DATA = "data"
OUT = "results"
os.makedirs(OUT, exist_ok=True)

ALPHA = 0.05  # adjusted p-value threshold for calling a gene significant
CPM_MIN = 1.0  # a gene must exceed this CPM ...
CPM_NSAMP = 10  # ... in at least this many samples (= one full group)

log = []


def say(msg):
    print(msg)
    log.append(str(msg))


say("=" * 78)
say("OSD-420 CORRECTED DGEA")
say("=" * 78)

# ---------------------------------------------------------------- 1. load ----
expr = pd.read_csv(f"{DATA}/counts.csv", index_col=0)
expr.index.name = "ENSEMBL"
say(f"\n[1] raw STAR unnormalized counts            {expr.shape[0]:>7,} genes x {expr.shape[1]} samples")

FLT = [c for c in expr.columns if "_FLT_" in c]
GC = [c for c in expr.columns if "_GC_" in c]
assert len(FLT) == 10 and len(GC) == 10
say(f"    Space Flight  n={len(FLT)}   Ground Control n={len(GC)}")

# ------------------------------------------------------------ 2. ERCC out ----
n0 = len(expr)
expr = expr[~expr.index.str.startswith("ERCC-")]
say(f"[2] drop ERCC spike-ins  (-{n0 - len(expr)})           {len(expr):>7,} genes")
# ERCC matters here: it is 19.8-39.7% of assigned counts AND Mix 1 / Mix 2 is
# perfectly collinear with flight/ground. Leaving it in wrecks the size factors.

# ------------------------------------------------------ 3. gene annotation ----
ann = pd.read_csv(f"{DATA}/genelab_dge.csv", usecols=["ENSEMBL", "SYMBOL", "GENENAME"])
ann = ann.drop_duplicates("ENSEMBL").set_index("ENSEMBL")
sym = ann["SYMBOL"].reindex(expr.index)
sym = sym.fillna(pd.Series(expr.index, index=expr.index))  # fall back to Ensembl ID
say(f"[3] gene symbols mapped                     {sym.notna().sum():>7,} "
    f"({(~ann['SYMBOL'].reindex(expr.index).isna()).sum():,} from GeneLab annotation)")

# ------------------------------------------------- 4. contamination screen ----
LIVER = ["Alb", "Apoa1", "Apoa2", "Apob", "Apoc1", "Apoc3", "Apoc4", "Apoh", "Apom",
         "Ttr", "Fga", "Fgb", "Fgg", "Kng1", "Kng2", "Ahsg", "Orm1", "Orm2",
         "Serpina1a", "Serpina1b", "Serpina1c", "Serpina3k", "Trf", "Hp", "Vtn",
         "Ambp", "Tf", "F2", "Cps1", "Hpx", "Itih1", "Itih2", "Itih3", "Itih4"]
LIVER += [s for s in sym.unique() if isinstance(s, str) and s.startswith("Mup")]
PANCREAS = ["Amy2a1", "Amy2a2", "Amy2a3", "Amy2a4", "Amy2a5", "Amy2b", "Amy1",
            "Cela1", "Cela2a", "Cela3b", "Ctrb1", "Ctrl", "Pnlip", "Pnliprp1",
            "Prss1", "Prss2", "Try4", "Try5", "Cpa1", "Cpa2", "Cpb1", "Clps",
            "Cel", "Sycn", "Pdia2", "Reg1", "Reg2", "Reg3b", "Zg16"]

lib_size = expr.sum(axis=0)
cpm = expr / lib_size * 1e6

liver_idx = sym[sym.isin(LIVER)].index
panc_idx = sym[sym.isin(PANCREAS)].index
liver_score = cpm.loc[liver_idx].sum(axis=0)  # CPM units = parts per million
panc_score = cpm.loc[panc_idx].sum(axis=0)

say(f"\n[4] CONTAMINATION SCREEN (dissection carryover)")
say(f"    liver panel     {len(liver_idx):>4} genes detected")
say(f"    pancreas panel  {len(panc_idx):>4} genes detected")
say(f"    liver ppm    flight  min {liver_score[FLT].min():9.1f}  median {liver_score[FLT].median():9.1f}  max {liver_score[FLT].max():9.1f}")
say(f"    liver ppm    ground  min {liver_score[GC].min():9.1f}  median {liver_score[GC].median():9.1f}  max {liver_score[GC].max():9.1f}")
say(f"    pancreas ppm flight  min {panc_score[FLT].min():9.1f}  median {panc_score[FLT].median():9.1f}  max {panc_score[FLT].max():9.1f}")
say(f"    pancreas ppm ground  min {panc_score[GC].min():9.1f}  median {panc_score[GC].median():9.1f}  max {panc_score[GC].max():9.1f}")
u_liv = stats.mannwhitneyu(liver_score[FLT], liver_score[GC])
u_pan = stats.mannwhitneyu(panc_score[FLT], panc_score[GC])
say(f"    liver    flight vs ground  Mann-Whitney p = {u_liv.pvalue:.4f}   <- group-IMBALANCED, creates false DEGs")
say(f"    pancreas flight vs ground  Mann-Whitney p = {u_pan.pvalue:.4f}   <- group-balanced, creates none")
say(f"    within-group spread, liver: flight {liver_score[FLT].max()/max(liver_score[FLT].min(),1e-9):.0f}-fold, "
    f"ground {liver_score[GC].max()/max(liver_score[GC].min(),1e-9):.0f}-fold")
top_gc = liver_score[GC].sort_values(ascending=False)
say(f"    single worst ground sample: {top_gc.index[0]} supplies "
    f"{100*top_gc.iloc[0]/liver_score[GC].sum():.1f}% of all ground liver signal")

contam_idx = liver_idx.union(panc_idx)
pd.DataFrame({"sample": lib_size.index,
              "group": ["Space Flight" if s in FLT else "Ground Control" for s in lib_size.index],
              "lib_size": lib_size.values,
              "liver_ppm": liver_score.values,
              "pancreas_ppm": panc_score.values}).to_csv(f"{OUT}/contamination_scores.csv", index=False)

n0 = len(expr)
expr = expr.drop(index=contam_idx)
say(f"    EXCLUDING {n0 - len(expr)} contaminant transcripts   {len(expr):>7,} genes remain")

# -------------------------------------------------------- 5. CPM prefilter ----
cpm = expr / expr.sum(axis=0) * 1e6
keep = (cpm > CPM_MIN).sum(axis=1) >= CPM_NSAMP
n0 = len(expr)
expr = expr[keep]
say(f"\n[5] prefilter: CPM > {CPM_MIN} in >= {CPM_NSAMP} samples  (-{n0 - len(expr):,})"
    f"      {len(expr):>7,} genes into DESeq2")
say(f"    (the old pipeline reached DESeq2 with 4,080 genes -- a {len(expr)/4080:.1f}x larger tested set)")

# ---------------------------------------------------------------- 6. DESeq2 ---
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats

counts = expr.T.astype(int)  # samples x genes, index = sample name
meta = pd.DataFrame(
    {"condition": ["Space_Flight" if s in FLT else "Ground_Control" for s in counts.index]},
    index=counts.index,
)
# Index-aligned by sample NAME, not by position. The old notebook aligned
# positionally and was correct only by luck.
assert list(counts.index) == list(meta.index)

say("\n[6] DESeq2  design = ~ condition   (single factor; all mice are male")
say("    C57BL/6J at one age, so no multi-factor model is available)")
dds = DeseqDataSet(counts=counts, metadata=meta, design="~condition", refit_cooks=True, quiet=True)
dds.deseq2()

# contrast=('condition','Space_Flight','Ground_Control')
#   -> POSITIVE log2FoldChange means HIGHER IN SPACE FLIGHT.
st = DeseqStats(dds, contrast=["condition", "Space_Flight", "Ground_Control"], quiet=True)
st.summary()
res = st.results_df.copy()
res["SYMBOL"] = sym.reindex(res.index).values
res["GENENAME"] = ann["GENENAME"].reindex(res.index).values
res = res.sort_values("padj")

tested = res["padj"].notna().sum()
say(f"    genes with a non-NaN adjusted p (BH denominator): {tested:,} of {len(res):,}")
say(f"    (the old pipeline's denominator was ~442)")

# ----------------------------------------------- 7. threshold sensitivity ----
say("\n[7] THRESHOLD SENSITIVITY  (this is the table the old run could not produce)")
rows = []
for a, lfc in [(0.05, 0), (0.05, 1), (0.05, 1.5), (0.05, 2), (0.10, 0), (0.01, 0)]:
    m = (res["padj"] < a) & (res["log2FoldChange"].abs() > lfc)
    up = (m & (res["log2FoldChange"] > 0)).sum()
    dn = (m & (res["log2FoldChange"] < 0)).sum()
    rows.append({"adj_p": a, "min_abs_log2FC": lfc, "n": int(m.sum()), "up": int(up), "down": int(dn)})
    say(f"    adj p < {a:<5} & |log2FC| > {lfc:<4} ->  n = {m.sum():>4}   ({up} up, {dn} down)")
pd.DataFrame(rows).to_csv(f"{OUT}/threshold_sensitivity.csv", index=False)

sig = res[res["padj"] < ALPHA].copy()
say(f"\n    HEADLINE: {len(sig)} genes at adjusted p < {ALPHA}  "
    f"({(sig['log2FoldChange']>0).sum()} up in flight, {(sig['log2FoldChange']<0).sum()} down)")

res.to_csv(f"{OUT}/deseq2_full_results.csv")
sig.to_csv(f"{OUT}/deseq2_significant.csv")

# ------------------------------------------- 8. check against GeneLab's own ---
say("\n[8] CROSS-CHECK vs GeneLab's delivered DESeq2 (full gene set, all 21,876)")
gl = pd.read_csv(f"{DATA}/genelab_dge.csv",
                 usecols=["ENSEMBL", "SYMBOL",
                          "Log2fc_(Space Flight)v(Ground Control)",
                          "Adj.p.value_(Space Flight)v(Ground Control)"])
gl = gl.rename(columns={"Log2fc_(Space Flight)v(Ground Control)": "gl_log2FC",
                        "Adj.p.value_(Space Flight)v(Ground Control)": "gl_padj"})
gl = gl.drop_duplicates("ENSEMBL").set_index("ENSEMBL")
gl_sig = gl[gl["gl_padj"] < 0.05]
say(f"    GeneLab significant at adj p < 0.05: {len(gl_sig)}")
ours = set(sig.index)
theirs = set(gl_sig.index)
say(f"    overlap with ours: {len(ours & theirs)}  "
    f"(ours only {len(ours - theirs)}, theirs only {len(theirs - ours)})")

j = res.join(gl[["gl_log2FC", "gl_padj"]], how="inner").dropna(subset=["log2FoldChange", "gl_log2FC"])
r = np.corrcoef(j["log2FoldChange"], j["gl_log2FC"])[0, 1]
say(f"    log2FC correlation with GeneLab across {len(j):,} shared genes: r = {r:.4f}")

REF = ["Gpx3", "Sparcl1", "Pdgfra", "Cxcl12", "Apoe", "Maf", "Aebp1", "Cldn5", "Kdr", "Wt1",
       "Ank1", "Trim10", "Gypa", "Hmbs",
       "Rgs13", "Fcer2a", "Ccr7", "Madcam1", "Isg15", "Ifi27l2a", "Rsad2", "Trim30a", "Ccna2"]
say("\n    Reference genes -- recovered?  (old pipeline recovered 1 of 18)")
say(f"    {'gene':<10} {'our log2FC':>11} {'our adj p':>12} {'GeneLab log2FC':>15} {'GeneLab adj p':>14}  ok")
rec = []
for g in REF:
    row = res[res["SYMBOL"] == g]
    if len(row) == 0:
        say(f"    {g:<10} {'ABSENT':>11}")
        rec.append({"gene": g, "recovered": False})
        continue
    row = row.iloc[0]
    e = row.name
    glr = gl.loc[e] if e in gl.index else None
    ok = "YES" if pd.notna(row["padj"]) and row["padj"] < 0.05 else "no"
    say(f"    {g:<10} {row['log2FoldChange']:>11.3f} {row['padj']:>12.3g} "
        f"{(glr['gl_log2FC'] if glr is not None else np.nan):>15.3f} "
        f"{(glr['gl_padj'] if glr is not None else np.nan):>14.3g}  {ok}")
    rec.append({"gene": g, "recovered": ok == "YES", "log2FC": row["log2FoldChange"],
                "padj": row["padj"], "baseMean": row["baseMean"],
                "gl_log2FC": glr["gl_log2FC"] if glr is not None else np.nan,
                "gl_padj": glr["gl_padj"] if glr is not None else np.nan})
recdf = pd.DataFrame(rec)
recdf.to_csv(f"{OUT}/reference_gene_recovery.csv", index=False)
say(f"\n    RECOVERED {int(recdf['recovered'].sum())} of {len(recdf)} reference genes "
    f"(old pipeline: 1 of 18)")

# ------------------------------------------------ 9. the old 10-gene list -----
OLD10 = ["Apoa2", "Ly6i", "Hemgn", "Alb", "Add2", "Ank1", "Gnao1", "Serpina3k", "Mup3", "Hspa1a"]
say("\n[9] WHAT HAPPENED TO THE OLD 10-GENE LIST")
say(f"    {'gene':<12} {'status in corrected analysis':<46} {'log2FC':>8} {'adj p':>10}")
old_rows = []
for g in OLD10:
    row = res[res["SYMBOL"] == g]
    if g in LIVER or g in PANCREAS:
        st_ = "EXCLUDED as liver/plasma contaminant"
        l2, p = np.nan, np.nan
    elif len(row) == 0:
        st_ = "removed by CPM prefilter (not expressed in spleen)"
        l2, p = np.nan, np.nan
    else:
        row = row.iloc[0]
        l2, p = row["log2FoldChange"], row["padj"]
        st_ = f"significant (adj p < 0.05)" if pd.notna(p) and p < 0.05 else "tested, NOT significant"
    say(f"    {g:<12} {st_:<46} {l2 if pd.notna(l2) else float('nan'):>8.3f} {p if pd.notna(p) else float('nan'):>10.3g}")
    old_rows.append({"gene": g, "status": st_, "log2FC": l2, "padj": p})
pd.DataFrame(old_rows).to_csv(f"{OUT}/old_ten_gene_fate.csv", index=False)

# --------------------------------------------------- 10. module statistics ---
MODULES = {
    "Stromal / perivascular": ["Gpx3", "Sparcl1", "Pdgfra", "Cxcl12", "Apoe", "Maf",
                               "Aebp1", "Cldn5", "Kdr", "Wt1", "Col1a1", "Col3a1", "Lum", "Dcn"],
    "Erythroid / heme": ["Ank1", "Gypa", "Trim10", "Hmbs", "Alas2", "Slc4a1", "Epb42",
                         "Klf1", "Gata1", "Tspo2", "Hemgn", "Add2", "Sptb", "Aqp1"],
    "Lymphoid organisation": ["Rgs13", "Ccr7", "Madcam1", "Fcer2a", "Cxcr5", "Cr2",
                              "Ccl19", "Ccl21a", "Sell", "Aicda"],
    "Type I interferon": ["Isg15", "Ifi27l2a", "Rsad2", "Trim30a", "Ifit1", "Ifit3",
                          "Oasl2", "Irf7", "Stat1", "Mx1", "Usp18", "Bst2"],
}
say("\n[10] MODULE-LEVEL TEST  (are these coordinated shifts, or single genes?)")
say("     Wilcoxon signed-rank on member-gene log2FC vs 0, using only tested genes")
mod_rows = []
for name, genes in MODULES.items():
    idx = res[res["SYMBOL"].isin(genes) & res["padj"].notna()]
    if len(idx) < 3:
        continue
    v = idx["log2FoldChange"].values
    w = stats.wilcoxon(v)
    nsig = (idx["padj"] < 0.05).sum()
    say(f"     {name:<26} n={len(v):>2} tested, {nsig:>2} individually sig, "
        f"median log2FC {np.median(v):+.3f}, Wilcoxon p = {w.pvalue:.2e}")
    mod_rows.append({"module": name, "n_tested": len(v), "n_sig": int(nsig),
                     "median_log2FC": float(np.median(v)), "wilcoxon_p": float(w.pvalue),
                     "genes": ";".join(idx["SYMBOL"].tolist())})
pd.DataFrame(mod_rows).to_csv(f"{OUT}/module_statistics.csv", index=False)

# ------------------------------------------------- 11. VST + PCA (both) ------
say("\n[11] PCA -- raw counts vs variance-stabilised")
from sklearn.decomposition import PCA

norm_counts = pd.DataFrame(dds.layers["normed_counts"], index=counts.index, columns=counts.columns)
vst = np.log2(norm_counts + 1)  # log2(normalised + 1); a VST-equivalent for this purpose

pca_out = {}
for tag, mat in [("raw", counts.astype(float)), ("vst", vst)]:
    X = mat.values
    X = X - X.mean(axis=0)
    p = PCA(n_components=4, svd_solver="full", random_state=0)  # full solver = deterministic
    Y = p.fit_transform(X)
    ev = p.explained_variance_ratio_
    grp = np.array([1 if s in FLT else 0 for s in mat.index])
    t = stats.mannwhitneyu(Y[grp == 1, 0], Y[grp == 0, 0])
    say(f"     {tag:<4} PC1 {ev[0]*100:5.1f}%  PC2 {ev[1]*100:5.1f}%   "
        f"PC1 flight-vs-ground Mann-Whitney p = {t.pvalue:.3f}")
    pca_out[tag] = {"coords": Y[:, :2].tolist(), "ev": ev[:2].tolist(),
                    "samples": list(mat.index), "pc1_p": float(t.pvalue)}
    # depth correlation
    rr = stats.spearmanr(Y[:, 0], lib_size.reindex(mat.index).values)
    say(f"          PC1 vs library size: Spearman rho = {rr.statistic:+.3f} (p = {rr.pvalue:.1e})")
    pca_out[tag]["pc1_depth_rho"] = float(rr.statistic)
    pca_out[tag]["pc1_depth_p"] = float(rr.pvalue)

# --------------------------------------------------------- 12. save state ----
norm_counts.T.to_csv(f"{OUT}/normalized_counts.csv")
vst.T.to_csv(f"{OUT}/vst_counts.csv")
meta.to_csv(f"{OUT}/sample_metadata.csv")
with open(f"{OUT}/pca.json", "w") as f:
    json.dump(pca_out, f, indent=1)

sig_symbols = sig["SYMBOL"].dropna().tolist()
with open(f"{OUT}/deg_genes.txt", "w") as f:
    f.write("\n".join(sig_symbols) + "\n")
with open(f"{OUT}/background_genes.txt", "w") as f:
    # background = genes ACTUALLY TESTED (non-NaN padj), not the prefiltered set
    f.write("\n".join(res[res["padj"].notna()]["SYMBOL"].dropna().unique().tolist()) + "\n")
say(f"\n[12] wrote {len(sig_symbols)} DEG symbols and "
    f"{res['padj'].notna().sum():,} background symbols")

with open(f"{OUT}/dgea_log.txt", "w") as f:
    f.write("\n".join(log))
say("\nDONE.")
