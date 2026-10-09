# When the Spleen Stops Building

Stromal remodelling and the loss of blood and immune cell production in spaceflight.

This is the work of The Spleen Machine (Kireeti, Pranav, Aryan and Vedant), a four-person team from Interlake High School in Bellevue, WA, in the 2026 NASA GeneLab for High Schools (GL4HS) capstone program. We re-analysed public RNA-seq data from the spleens of mice flown on NASA's Rodent Research-9 mission and used the results to propose follow-up experiments.

Our abstract was accepted for the High School/Middle School Student Poster Session at the ASGSR 2026 Annual Meeting (American Society for Gravitational and Space Research) in Crystal City, VA. The student poster session is on December 5, 2026.

## The question

Astronauts come home with weaker immune systems. In mice, spaceflight shrinks the spleen and reduces every major splenic leukocyte population. Nobody knows yet whether the immune cells themselves are damaged or whether the stromal scaffold that organises where blood and immune cells are made gets remodelled. The RR-9 spleens were collected through NASA's Biospecimen Sharing Program while the main study looked at eyes, joints and fluid shifts, which left their gene expression open for a closer look.

## Dataset

[OSD-420](https://osdr.nasa.gov/bio/repo/data/studies/OSD-420) (GLDS-420) from NASA's Open Science Data Repository, doi:[10.26030/k030-ms28](https://doi.org/10.26030/k030-ms28).

- 20 male C57BL/6J mice, 10 weeks old at launch: 10 flight, 10 ground control
- 33 days in the ISS Rodent Habitat, launched August 14, 2017 on SpaceX CRS-12
- QIAseq UPX 3' Transcriptome libraries (a 3' tag protocol), 93 bp single-end reads on a NovaSeq 6000, with ERCC spike-ins

**The confound.** Hurricane Irma cancelled the original ground-control run, so the ground controls were a separate cohort dissected nine months after the flight animals. Group, cohort, dissection date and ERCC spike-in mix are perfectly collinear, and no statistical adjustment can separate them. We report every result with that limitation attached, and the proposed experiments use a controlled ground analog because of it.

## Findings

Our re-analysis found 146 genes at adjusted p < 0.05 out of 10,546 tested, 83 higher in flight and 63 lower. As a cross-check, 57 of the 80 genes in GeneLab's own analysis of this dataset are among them, and fold changes agree closely between the two (r = 0.86).

Three groups of genes move together, and each one stands out from the rest of the dataset as a block (rank-sum test against all tested genes):

- Stromal and perivascular genes go up (p = 1.3 x 10^-7). All 10 genes in the module are individually significant, including Gpx3, Sparcl1, Pdgfra and Cxcl12. Gpx3 is the strongest single result (log2FC +0.91, adjusted p = 7.0 x 10^-16), and we found no earlier report of it changing in any spaceflight tissue.
- Erythroid and heme-synthesis genes go down (p = 2.3 x 10^-5): Trim10, Gypa and Hmbs, along with most of the heme biosynthesis pathway.
- Type I interferon genes go down (p = 6.6 x 10^-7): Isg15, Ifi27l2a, Rsad2 and others. This matches Wu et al. (Nature Communications, 2024), who used this dataset to check findings from human immune cells.

Lymphoid organisation genes such as Rgs13 and Ccr7 also fall one by one, but that module does not separate from background as a block (p = 0.059), so we treat it as supporting detail.

Pathway analysis (25 GSEA terms and 65 ORA terms passing our cutoffs) shows the same picture. TGF-beta and BMP signalling and matrix remodelling go up in flight. Heme metabolism, interferon signalling and proliferation (E2F targets, G2-M checkpoint) go down. Read together, the spleen looks like it is shifting from an organ that actively makes blood and immune cells toward a quieter, stroma-dominated one.

We also learned a lot from our first pass, which reported only ten genes. Its filters (a coefficient-of-variation cutoff and |log2FC| > 2) kept mostly genes with near-zero counts, and its "hepatic lipidosis" and cholesterol-transport hits turned out to be liver tissue carried over during dissection. None of those ten genes holds up in the corrected analysis; `results/old_ten_gene_fate.csv` shows what happened to each one.

## Hypothesis and proposed aims

We propose that spaceflight remodels the splenic stromal niche, and that this remodelling, rather than direct damage to leukocytes, drives the loss of red cell production, germinal-centre organisation and interferon tone behind post-flight immune decline.

All three aims use hindlimb unloading, a ground-based spaceflight analog, and each stands on its own:

1. Find out whether the erythroid decline is a real loss of red cell production in the spleen or just less residual blood, using perfused spleens, Ter119/CD71 flow cytometry and CFU-E colony assays.
2. Test whether stromal expansion disorganises germinal-centre architecture, using single-nucleus RNA-seq, immunofluorescence, and NP-KLH immunisation with germinal-centre scoring.
3. Test whether the lower interferon signature means weaker antiviral defence, using ex vivo poly(I:C) and IFN-beta stimulation of splenocytes and an in vivo viral challenge.

Our ASGSR abstract is in [`docs/asgsr-2026-abstract.md`](docs/asgsr-2026-abstract.md) and our capstone showcase slides are in [`docs/capstone-showcase-slides.pdf`](docs/capstone-showcase-slides.pdf). The specific aims page in [`docs/specific-aims.pdf`](docs/specific-aims.pdf) was written in July, before the corrected analysis, so its gene count (80) and its third aim differ from what is described here.

## Repository layout

```
.
├── README.md
├── LICENSE
├── CITATION.cff
├── requirements.txt
├── docs/
│   ├── asgsr-2026-abstract.md        abstract accepted to ASGSR 2026
│   ├── capstone-showcase-slides.pdf  GL4HS capstone showcase deck
│   └── specific-aims.pdf             one-page specific aims (July draft)
├── notebooks/
│   ├── NB6_CORRECTED_OSD420_dgea.ipynb      QC, contamination screen, differential expression
│   ├── NB7_CORRECTED_OSD420_pathways.ipynb  GSEA and over-representation analysis
│   ├── NB8_figures_from_results.ipynb       data figures
│   ├── NB9_schematic_figures.ipynb          drawn figures
│   └── README.md                            run order and which notebook makes which figure
├── scripts/                          the same pipelines as plain Python, plus the deck builder
├── results/                          every table the notebooks write
│   └── pathways/                     GSEA and ORA output, with member genes
└── figures/                          300 dpi PNGs, SVG source for the schematics
```

## Running it

The notebooks run in Google Colab with no setup. Notebook 6 downloads the counts and metadata straight from NASA OSDR, and each notebook installs what it needs in its first cell. Run them in order: 6, then 7 (about 20 minutes, almost all GSEA permutations), then 8. Notebook 9 has no data dependency.

To run locally instead:

```
pip install -r requirements.txt
python scripts/01_dgea_corrected.py
python scripts/02_pathway_corrected.py
python scripts/03_figures_data.py
python scripts/04_schematics.py
```

Run the scripts from the repository root. Raw data goes into `data/`, which git ignores.

Methods in brief: ERCC spike-ins and a 71-transcript liver and pancreas carryover panel are removed, genes need CPM > 1 in at least 10 samples, and differential expression uses PyDESeq2 0.5.4 (design `~ condition`; positive log2FC means higher in flight). GSEA uses gseapy 1.3.1 with phenotype permutation on normalised counts across GO, MSigDB Hallmark and Reactome, filtered at FDR q < 0.25 and FWER < 0.25. ORA uses the tested genes as background.

## Acknowledgements

Thanks to the NASA GeneLab for High Schools program and its instructors for the training and the original Colab analysis notebooks this work started from, and to the RR-9 investigators and the Biospecimen Sharing Program for making the spleen data public.

## Citation

If you use this work, please cite the dataset:

Galazka JM, et al. Transcriptional profiling of spleens from mice flown on the RR-9 mission. NASA Open Science Data Repository, OSD-420, version 4 (2021). doi:10.26030/k030-ms28

and this repository (see [`CITATION.cff`](CITATION.cff)).
