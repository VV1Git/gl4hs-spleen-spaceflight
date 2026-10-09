#!/usr/bin/env python3
"""
OSD-420 -- CORRECTED pathway analysis (GSEA + ORA).

Replaces Notebook 7 (`420_parameterized_performing_gsea_and_ora`).

WHAT CHANGED VS THE TEAM'S VERSION, AND WHY
-------------------------------------------
1. FIXED the background bug. The old `run_ora()` accepted a `background_genes`
   argument and then never passed it to `gp.enrichr`, so every ORA p-value was
   computed against Enrichr's whole-genome default. Background is now the genes
   ACTUALLY TESTED by DESeq2 (non-NaN adjusted p), which is the correct universe.

2. `permutation_type='phenotype'`, not `'gene_set'`. The old notebook's own
   comment said to use phenotype with >= 15 samples; there are 20. Gene-set
   permutation destroys gene-gene correlation structure, so any co-regulated
   block -- e.g. one contaminating tissue -- scores as wildly significant.

3. GSEA runs on DESeq2 NORMALISED counts, not raw counts. signal_to_noise on raw
   counts conflates expression with library size.

4. Gene-set size is BOUNDED (min 15, max 300). The old run used min_size=5 on GO
   and the gseapy default of 15 on GEO -- drift inside a single notebook -- and
   never set max_size, so 500+ member sets were eligible against a 10-gene list.

5. Terms are filtered on FDR q < 0.25 AND FWER < 0.25. The old run used FWER
   alone and reported terms at q = 0.27 and q = 0.35 as significant.

6. ORA reports Overlap and Odds Ratio, so gene-set size and fold enrichment are
   available -- both are required by the course and neither was reportable before.

7. Terms with fewer than 3 overlapping genes are dropped. Six of the old run's
   ten GO terms were single-gene overlaps, and the gene was APOA2 (a contaminant).

8. Every reported term's member genes are written back out with their actual
   log2FC and adjusted p -- the "download-to-Excel loop" the lecture calls the
   single most important procedural step.
"""

import json
import os

import gseapy as gp
import numpy as np
import pandas as pd
from scipy import stats

OUT = "results"
os.makedirs(f"{OUT}/pathways", exist_ok=True)

ALPHA = 0.05
FDR_T = 0.25
FWER_T = 0.25
MIN_SET, MAX_SET = 15, 300
MIN_OVERLAP = 3
SEED = 7

log = []


def say(m):
    print(m)
    log.append(str(m))


say("=" * 78)
say("OSD-420 CORRECTED PATHWAY ANALYSIS")
say("=" * 78)

res = pd.read_csv(f"{OUT}/deseq2_full_results.csv", index_col=0)
norm = pd.read_csv(f"{OUT}/normalized_counts.csv", index_col=0)   # genes x samples
meta = pd.read_csv(f"{OUT}/sample_metadata.csv", index_col=0)

tested = res[res["padj"].notna()].copy()
sig = tested[tested["padj"] < ALPHA].copy()
say(f"\ntested genes (non-NaN adj p): {len(tested):,}")
say(f"significant at adj p < {ALPHA}: {len(sig)}  "
    f"({(sig['log2FoldChange']>0).sum()} up, {(sig['log2FoldChange']<0).sum()} down)")

# symbol-level table, collapsing duplicate symbols to the highest-baseMean row
t = tested.dropna(subset=["SYMBOL"]).sort_values("baseMean", ascending=False)
t = t[~t["SYMBOL"].duplicated()]
say(f"unique gene symbols after collapsing duplicates by highest baseMean: {len(t):,}")

background = t["SYMBOL"].tolist()
sig_t = t[t["padj"] < ALPHA]
up_list = sig_t[sig_t["log2FoldChange"] > 0]["SYMBOL"].tolist()
dn_list = sig_t[sig_t["log2FoldChange"] < 0]["SYMBOL"].tolist()
all_list = sig_t["SYMBOL"].tolist()
say(f"\nGENE LISTS FOR ENRICHMENT (course sweet spot is 10-50, up to ~100)")
say(f"   all significant : {len(all_list)}")
say(f"   UP in flight    : {len(up_list)}")
say(f"   DOWN in flight  : {len(dn_list)}")
say("   -> analysing UP and DOWN separately; an asymmetric split is the")
say("      informative case, and a merged list cancels direction.")

lookup = t.set_index("SYMBOL")[["log2FoldChange", "padj", "baseMean"]]

LIBS = ["GO_Biological_Process_2025", "GO_Cellular_Component_2025",
        "MSigDB_Hallmark_2020", "Reactome_Pathways_2024"]

# =========================================================== 1. GSEA =========
say("\n" + "-" * 78)
say("[A] GSEA  -- normalised counts, phenotype permutation, seed=7")
say("-" * 78)

expr = norm.copy()
expr.index = res["SYMBOL"].reindex(expr.index).values
expr = expr[~pd.isna(expr.index)]
expr = expr.groupby(level=0).max()          # collapse duplicate symbols by max, not mean
expr = expr.loc[[g for g in expr.index if g in set(background)]]
cls = ["Space_Flight" if "_FLT_" in s else "Ground_Control" for s in expr.columns]
say(f"    matrix {expr.shape[0]:,} genes x {expr.shape[1]} samples; "
    f"{cls.count('Space_Flight')} flight / {cls.count('Ground_Control')} ground")
say(f"    positive NES = higher in SPACE FLIGHT")

gsea_all = []
for lib in LIBS:
    say(f"    running {lib} ...")
    r = gp.gsea(data=expr, gene_sets=lib, cls=cls,
                permutation_type="phenotype", permutation_num=1000,
                method="signal_to_noise", min_size=MIN_SET, max_size=MAX_SET,
                threads=2, seed=SEED, outdir=None, no_plot=True)
    d = r.res2d.copy()
    d["Library"] = lib
    gsea_all.append(d)
    say(f"        {len(d)} gene sets scored")

g = pd.concat(gsea_all, ignore_index=True)
for c in ["NES", "ES", "NOM p-val", "FDR q-val", "FWER p-val"]:
    g[c] = pd.to_numeric(g[c], errors="coerce")
g.to_csv(f"{OUT}/pathways/gsea_all_scored.csv", index=False)

gs = g[(g["FDR q-val"] < FDR_T) & (g["FWER p-val"] < FWER_T)].copy()
gs = gs.sort_values("NES", key=abs, ascending=False)
say(f"\n    passing FDR q < {FDR_T} AND FWER < {FWER_T}: {len(gs)} terms "
    f"({(gs['NES']>0).sum()} up in flight, {(gs['NES']<0).sum()} down)")
gs.to_csv(f"{OUT}/pathways/gsea_significant.csv", index=False)

say(f"\n    {'NES':>7} {'FDR q':>9} {'FWER':>7}  Term")
for _, r_ in gs.head(25).iterrows():
    say(f"    {r_['NES']:>7.3f} {r_['FDR q-val']:>9.4f} {r_['FWER p-val']:>7.3f}  "
        f"{r_['Term'][:80]}")

# the download-to-Excel loop: member genes with their real fold changes
UP = {str(s_).upper(): s_ for s_ in lookup.index}   # gseapy uppercases gene symbols
rows = []
for _, r_ in gs.iterrows():
    for gene in str(r_["Lead_genes"]).split(";"):
        key = UP.get(gene.strip().upper())
        if key is not None:
            rows.append({"Term": r_["Term"], "Library": r_["Library"], "NES": r_["NES"],
                         "FDR_q": r_["FDR q-val"], "FWER": r_["FWER p-val"], "gene": key,
                         "log2FC": lookup.loc[key, "log2FoldChange"],
                         "adj_p": lookup.loc[key, "padj"],
                         "baseMean": lookup.loc[key, "baseMean"]})
led = pd.DataFrame(rows)
led.to_csv(f"{OUT}/pathways/gsea_leading_edge_genes.csv", index=False)
say(f"\n    leading-edge gene table written: {len(led)} gene-in-term rows")
if len(led):
    chk = led.groupby("Term").agg(n=("gene", "size"),
                                  median_log2FC=("log2FC", "median"),
                                  median_baseMean=("baseMean", "median")).sort_values("n", ascending=False)
    say("    sanity check -- do member genes actually move, and are they expressed?")
    say(f"    {'n':>3} {'med log2FC':>11} {'med baseMean':>13}  Term")
    for term, rr in chk.head(15).iterrows():
        say(f"    {int(rr['n']):>3} {rr['median_log2FC']:>+11.3f} {rr['median_baseMean']:>13.1f}  {term[:70]}")

# ============================================================ 2. ORA =========
say("\n" + "-" * 78)
say("[B] ORA  -- proper background, Overlap + Odds Ratio reported")
say("-" * 78)
say(f"    background = {len(background):,} genes actually tested by DESeq2")

# gseapy's enrichr does NOT return an "Overlap" column when a custom background is
# supplied, so set sizes are computed here from the libraries themselves, restricted
# to the tested background -- which is the size that actually matters for the test.
say("    fetching gene-set libraries to compute effective set sizes ...")
bgset = set(str(x).upper() for x in background)
SETSIZE = {}
for lib in LIBS:
    d_ = gp.get_library(name=lib, organism="Mouse")
    for term, genes in d_.items():
        SETSIZE[(lib, term)] = len(bgset & set(str(x).upper() for x in genes))

ora_all = []
for tag, lst in [("UP_in_flight", up_list), ("DOWN_in_flight", dn_list)]:
    if len(lst) < 5:
        continue
    say(f"\n    {tag}: {len(lst)} genes")
    e = gp.enrichr(gene_list=lst, gene_sets=LIBS, organism="mouse",
                   background=background, outdir=None)
    d = e.results.copy()
    d["direction"] = tag
    d["n_overlap"] = d["Genes"].apply(lambda g: len([x for x in str(g).split(";") if x.strip()]))
    d["set_size"] = [SETSIZE.get((gs_, t_), np.nan) for gs_, t_ in zip(d["Gene_set"], d["Term"])]
    d["Overlap"] = d["n_overlap"].astype(str) + "/" + d["set_size"].astype("Int64").astype(str)
    d["fold_enrichment"] = (d["n_overlap"] / len(lst)) / (d["set_size"] / len(background))
    ora_all.append(d)

o = pd.concat(ora_all, ignore_index=True)
o.to_csv(f"{OUT}/pathways/ora_all.csv", index=False)

os_ = o[(o["Adjusted P-value"] < ALPHA) &
        (o["n_overlap"] >= MIN_OVERLAP) &
        (o["set_size"].between(MIN_SET, MAX_SET))].copy()
os_ = os_.sort_values("Adjusted P-value")
say(f"\n    passing adj p < {ALPHA}, overlap >= {MIN_OVERLAP}, set size {MIN_SET}-{MAX_SET}: {len(os_)} terms")
os_.to_csv(f"{OUT}/pathways/ora_significant.csv", index=False)

say(f"\n    {'dir':<15} {'ovl':>8} {'fold':>6} {'OR':>7} {'adj p':>10}  Term")
for _, r_ in os_.head(30).iterrows():
    say(f"    {r_['direction']:<15} {r_['Overlap']:>8} {r_['fold_enrichment']:>6.1f} "
        f"{r_['Odds Ratio']:>7.1f} {r_['Adjusted P-value']:>10.3g}  {r_['Term'][:66]}")

rows = []
for _, r_ in os_.iterrows():
    for gene in str(r_["Genes"]).split(";"):
        gg = gene.strip()
        match = [UP[gg.upper()]] if gg.upper() in UP else []
        if match:
            rows.append({"Term": r_["Term"], "direction": r_["direction"],
                         "Overlap": r_["Overlap"], "fold_enrichment": r_["fold_enrichment"],
                         "OddsRatio": r_["Odds Ratio"],
                         "adj_p_term": r_["Adjusted P-value"], "gene": match[0],
                         "log2FC": lookup.loc[match[0], "log2FoldChange"],
                         "adj_p_gene": lookup.loc[match[0], "padj"],
                         "baseMean": lookup.loc[match[0], "baseMean"]})
pd.DataFrame(rows).to_csv(f"{OUT}/pathways/ora_member_genes.csv", index=False)
say(f"\n    ORA member-gene table written: {len(rows)} gene-in-term rows")

# ============================== 3. module tests, self-contained + competitive ==
say("\n" + "-" * 78)
say("[C] MODULE TESTS -- the three lines of evidence")
say("-" * 78)

MODULES = {
    "Stromal / perivascular (UP)": ["Gpx3", "Sparcl1", "Pdgfra", "Cxcl12", "Apoe", "Maf",
                                    "Aebp1", "Cldn5", "Kdr", "Wt1"],
    "Erythroid / heme (DOWN)": ["Ank1", "Gypa", "Trim10", "Hmbs", "Alas2", "Slc4a1",
                                "Epb42", "Klf1", "Tspo2", "Hemgn"],
    "Lymphoid organisation (DOWN)": ["Rgs13", "Ccr7", "Madcam1", "Fcer2a", "Cxcr5",
                                     "Cr2", "Ccl19", "Ccl21a"],
    "Type I interferon (DOWN)": ["Isg15", "Ifi27l2a", "Rsad2", "Trim30a", "Ifit1",
                                 "Ifit3", "Oasl2", "Irf7", "Stat1", "Bst2"],
}
allfc = t["log2FoldChange"].values
mod_rows = []
say(f"\n    {'module':<30} {'n':>3} {'sig':>4} {'median log2FC':>14} {'signed-rank p':>14} {'rank-sum p':>12}")
for name, genes in MODULES.items():
    sub = t[t["SYMBOL"].isin(genes)]
    if len(sub) < 3:
        continue
    v = sub["log2FoldChange"].values
    sr = stats.wilcoxon(v).pvalue                                   # self-contained
    rs = stats.mannwhitneyu(v, allfc, alternative="two-sided").pvalue  # competitive
    nsig = int((sub["padj"] < ALPHA).sum())
    say(f"    {name:<30} {len(v):>3} {nsig:>4} {np.median(v):>+14.3f} {sr:>14.2e} {rs:>12.2e}")
    mod_rows.append({"module": name, "n_tested": len(v), "n_significant": nsig,
                     "median_log2FC": float(np.median(v)),
                     "signed_rank_p": float(sr), "rank_sum_p": float(rs),
                     "genes": ";".join(sub["SYMBOL"]),
                     "detail": "; ".join(f"{r.SYMBOL} {r.log2FoldChange:+.2f} (p={r.padj:.1e})"
                                         for r in sub.itertuples())})
pd.DataFrame(mod_rows).to_csv(f"{OUT}/module_statistics.csv", index=False)

with open(f"{OUT}/pathway_log.txt", "w") as f:
    f.write("\n".join(log))
say("\nDONE.")
