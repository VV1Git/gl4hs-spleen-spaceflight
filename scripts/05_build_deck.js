// GL4HS 2026 Capstone Showcase — The Spleen Machine (OSD-420-3)
//
// Built to the Capstone Showcase Template 2026 content areas:
//   1  Title Slide
//   2  Background and Introduction
//   3-6 Data Analysis and Results
//   7-8 Hypothesis and Methodology
//   9  Conclusions and Significance
//   10 Thank you, Acknowledgements and Selected References
//
// Slides carry a figure, a headline and a few words. Everything else lives in
// the speaker notes, so the presenters do the explaining rather than the slide.
// White background throughout. Body text 22pt or larger; only captions,
// attribution and references are smaller.

const pptxgen = require("pptxgenjs");
const { imageSize: sizeOf } = require("image-size");
const fs = require("fs");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in
pres.author = "The Spleen Machine (OSD-420-3)";
pres.title = "When the Spleen Stops Building";

const SURFACE = "FFFFFF";
const INK = "171310";
const INK2 = "574E43";
const MUTED = "7A7065";
const LINE = "DED4C2";
const TEAL = "14876B";
const RUST = "A34517";
const PLUM = "7C42AB";
const TAUPE = "6B5B45";
const TEAL_L = "E2F2EC";
const RUST_L = "F8ECE3";
const PLUM_L = "EFE8F7";
const CARD = "F3EDE1";

const F = "Calibri";
const W = 13.333, H = 7.5;
const M = 0.55;

const T_TITLE = 34;
const T_BODY = 24;
const T_CAP = 15;
const T_ATTR = 12;

let slideNo = 0;

function fit(img, bx, by, bw, bh) {
  const d = sizeOf(fs.readFileSync(img));
  const ar = d.width / d.height;
  let w = bw, h = bw / ar;
  if (h > bh) { h = bh; w = bh * ar; }
  return { path: img, x: bx + (bw - w) / 2, y: by + (bh - h) / 2, w, h };
}

function slide() {
  const s = pres.addSlide();
  s.background = { color: SURFACE };
  slideNo += 1;
  const n = slideNo;
  s.addText(String(n), {
    x: W - 1.05, y: H - 0.68, w: 0.5, h: 0.34, fontFace: F, fontSize: 14,
    color: MUTED, align: "right", valign: "middle", margin: 0,
  });
  return s;
}

function head(s, title) {
  s.addText(title, {
    x: M, y: 0.34, w: W - 2 * M, h: 0.72, fontFace: F, fontSize: T_TITLE, bold: true,
    color: INK, align: "left", valign: "middle", margin: 0,
  });
}

function caption(s, x, y, w, text, attr) {
  s.addText(text, {
    x, y, w, h: 0.32, fontFace: F, fontSize: T_CAP, color: INK2, margin: 0, valign: "top",
  });
  if (attr) {
    s.addText(attr, {
      x, y: y + 0.33, w, h: 0.28, fontFace: F, fontSize: T_ATTR, color: MUTED,
      margin: 0, valign: "top", italic: true,
    });
  }
}

function card(s, x, y, w, h, fill, border) {
  s.addShape(pres.ShapeType.rect, {
    x, y, w, h, fill: { color: fill }, line: { color: border || fill, width: 1 },
  });
}

const ATTR_TEAM = "Image produced by The Spleen Machine for the 2026 Capstone Showcase.";
const ATTR_PLOT = "Plot produced by The Spleen Machine from NASA OSDR OSD-420.";

// ========================================================= 1. TITLE =========
{
  const s = slide();

  s.addText("NASA GENELAB FOR HIGH SCHOOLS  ·  2026 CAPSTONE", {
    x: M, y: 1.30, w: W - 2 * M, h: 0.38, fontFace: F, fontSize: 18, bold: true,
    color: TAUPE, charSpacing: 2.0, margin: 0,
  });
  s.addText("When the Spleen Stops Building", {
    x: M, y: 1.80, w: W - 2 * M, h: 1.05, fontFace: F, fontSize: 52, bold: true,
    color: INK, margin: 0, valign: "middle",
  });
  s.addText("Stromal remodelling and the loss of blood and immune cell production in spaceflight", {
    x: M, y: 2.92, w: 11.8, h: 0.55, fontFace: F, fontSize: 24, color: INK2, margin: 0,
  });
  s.addText("The Spleen Machine   ·   OSD-420 / GLDS-420   ·   RR-9 spleen", {
    x: M, y: 3.74, w: W - 2 * M, h: 0.46, fontFace: F, fontSize: 22, bold: true,
    color: TAUPE, margin: 0, valign: "middle",
  });

  ["Kireeti", "Pranav", "Aryan", "Vedant"].forEach((n, i) => {
    const x = M + i * 3.05;
    s.addText(n, { x, y: 4.76, w: 2.9, h: 0.42, fontFace: F, fontSize: 24, bold: true, color: INK, margin: 0 });
    s.addText("Interlake High School", { x, y: 5.20, w: 2.9, h: 0.34, fontFace: F, fontSize: 18, color: INK2, margin: 0 });
    s.addText("Bellevue, Washington", { x, y: 5.54, w: 2.9, h: 0.34, fontFace: F, fontSize: 18, color: INK2, margin: 0 });
  });

  s.addText("Dataset: NASA Open Science Data Repository OSD-420  ·  doi:10.26030/k030-ms28", {
    x: M, y: 6.52, w: W - 2 * M, h: 0.34, fontFace: F, fontSize: 15, color: MUTED, margin: 0,
  });

  s.addNotes(
`[0:15]  SPEAKER: Kireeti

"Good morning. We're The Spleen Machine, from Interlake High School in Bellevue, Washington.
Our project is called When the Spleen Stops Building, and we worked on OSD-420, the spleen
dataset from Rodent Research 9."

Hand straight to slide 2. Don't read the team list aloud.

TIMING (target 7:00, hard limit 8:00)
  1  Title ....................... 0:15   Kireeti
  2  Background .................. 1:00   Kireeti
  3  Methods and QC .............. 0:50   Pranav
  4  146 genes ................... 1:00   Pranav
  5  Three modules ............... 1:00   Aryan
  6  Pathways .................... 0:50   Aryan
  7  Hypothesis and aims ......... 0:50   Vedant
  8  Methodology ................. 0:50   Vedant
  9  Conclusions ................. 0:40   Kireeti
 10  Thanks and references ....... 0:25   all four
                                  -----
                                   7:00

DELIVERY
 · The slides are deliberately sparse. The content is yours to say, not to read.
 · Don't recite. These notes are prompts.
 · Slow down. Take a breath at each slide change.
 · Everyone speaks, and everyone must be able to cover anyone else's part and share the
   screen if a laptop dies. Rehearse one cold handoff.`);
}

// ================================================== 2. BACKGROUND ===========
{
  const s = slide();
  head(s, "Background and Introduction");

  s.addText("Astronauts come home immunosuppressed. Did the tissue change?", {
    x: M, y: 1.08, w: W - 2 * M, h: 0.50, fontFace: F, fontSize: 26, bold: true,
    color: TAUPE, margin: 0, valign: "middle",
  });

  const im = fit("figures/fig_mission.png", M, 1.72, W - 2 * M, 4.30);
  s.addImage(im);
  caption(s, M, 6.16, 11.4,
    "Figure 1. RR-9 study design, the spleen samples, and the cohort confound.", ATTR_TEAM);

  s.addNotes(
`[1:00]  SPEAKER: Kireeti

THE MISSION
 · Rodent Research 9. Twenty male C57BL/6J mice, SpaceX CRS-12, thirty-three days on the ISS.
   Ten flew in the Rodent Habitat, ten stayed on the ground. All ten weeks old at launch.
 · The spleen came out through the Biospecimen Sharing Program. RR-9's own papers are about
   eye pressure, joint degradation and fluid shifts. Nobody has looked at the spleen.

THE TISSUE
 · The spleen has two jobs that matter here. In the red pulp, mice make red blood cells —
   humans mostly stop doing this after birth, mice never do. In the white pulp, B cells and
   T cells are organised into separate zones so they can meet antigen properly.
 · So it is both a blood factory and an immune organising centre. If either fails, you would
   expect exactly the immune problems astronauts report.

WHAT IS ALREADY KNOWN
 · Gridley and colleagues, after STS-135, found the spleen shrinks and every major leukocyte
   population drops.
 · Pecaut and colleagues found the same pattern with elevated oxidative stress.
 · Han and colleagues found the expression profile looks like accelerated immune ageing.

THE GAP, and this is our whole project
 · Everyone has measured that the immune cells disappear. Nobody has established WHY.
 · Two possibilities. Either the immune cells themselves are being damaged, or the tissue
   scaffold that tells them where to live is being rebuilt underneath them.
 · Those are different problems with different countermeasures.

THE CONFOUND — say this out loud, do not wait to be asked
 · Hurricane Irma cancelled the Kennedy Space Center ground-control run. It was redone nine
   months later with a different cohort of mice.
 · So group, cohort, dissection date and library batch are all the same variable. No
   statistical adjustment separates them.
 · Two cohort controls were collected to fix exactly this, and never processed.
 · What that means: we cannot attribute a signal to microgravity from this dataset alone.
   That is why every one of our aims proposes a controlled ground experiment.`);
}

// ======================================= 3. DATA ANALYSIS: METHODS ==========
{
  const s = slide();
  head(s, "Data Analysis: what we checked first");

  const im1 = fit("figures/fig_pipeline.png", M, 1.30, W - 2 * M, 1.62);
  s.addImage(im1);
  caption(s, M, 2.98, 11.4, "Figure 2. Analysis pipeline.", ATTR_TEAM);

  const im2 = fit("figures/fig_qc_pca.png", M, 3.80, 7.30, 2.95);
  s.addImage(im2);
  caption(s, M, 6.80, 7.30, "Figure 3. Quality control before testing.", ATTR_PLOT);

  s.addText("Our biggest signal\nis sequencing depth,\nnot spaceflight.", {
    x: 8.35, y: 4.30, w: 4.45, h: 2.00, fontFace: F, fontSize: 26, bold: true,
    color: TAUPE, margin: 0, valign: "middle", lineSpacingMultiple: 1.10,
  });

  s.addNotes(
`[0:50]  SPEAKER: Pranav

WALK THE PIPELINE, left to right
 · Raw STAR counts from GeneLab: 57,278 genes across 20 samples.
 · Remove the ERCC spike-ins. This matters more here than usual, because Mix 1 went to every
   flight sample and Mix 2 went to every ground sample. Spike-in identity IS group. Leaving
   them in would corrupt the size factors in a group-dependent way.
 · Screen for dissection carryover. The spleen sits next to the liver and pancreas, and a
   trace of neighbouring tissue comes across on the blade. We scored a liver panel and a
   pancreas panel in every sample and removed 71 transcripts before testing anything.
 · Expression filter: a gene has to exceed one count per million in at least ten samples,
   which is one whole group. That leaves 14,475 genes into DESeq2, of which 10,546 get an
   adjusted p-value.

WHAT WE DELIBERATELY DID NOT DO — this is the important part
 · No variance filter before testing. Point at the left plot. Before touching biology we asked
   what our biggest axis of variation actually was, and on raw counts it is library size, with
   a Spearman correlation of 0.99. Any filter applied to raw counts inherits that. A
   variance filter would have been a sequencing-depth filter wearing a disguise.
 · No fold-change gate to select genes.
 · No TPM or FPKM. This is 3-prime tag data, so every transcript contributes about one
   fragment regardless of gene length. Length normalisation is meaningless here.
 · No raw p-values anywhere.

THE HONEST RESULT — point at the right plot
 · After normalising, flight and ground do not separate. p = 0.38.
 · We are showing you that rather than hiding it, because it sets the expectation for the next
   three slides: this is a subtle, coordinated effect, not a dramatic one.

If asked why the carryover matters: pancreatic transcripts hit tens of thousands of counts in
three samples but produce zero differentially expressed genes, because they happen to be
balanced across groups. The liver panel is the same phenomenon but group-imbalanced, which is
exactly how a false result gets made.`);
}

// ======================================= 4. DATA ANALYSIS: DEGs =============
{
  const s = slide();
  head(s, "Data Analysis: 146 genes change in flight spleen");

  const im = fit("figures/fig_volcano.png", M, 1.20, 7.30, 5.10);
  s.addImage(im);
  caption(s, M, 6.44, 7.30, "Figure 4. Differential expression, DESeq2.", ATTR_PLOT);

  s.addText("83", { x: 8.30, y: 1.60, w: 4.4, h: 1.05, fontFace: F, fontSize: 66, bold: true, color: TEAL, margin: 0, valign: "bottom" });
  s.addText("higher in flight", { x: 8.30, y: 2.68, w: 4.4, h: 0.44, fontFace: F, fontSize: 24, color: INK2, margin: 0 });
  s.addText("63", { x: 8.30, y: 3.44, w: 4.4, h: 1.05, fontFace: F, fontSize: 66, bold: true, color: RUST, margin: 0, valign: "bottom" });
  s.addText("lower in flight", { x: 8.30, y: 4.52, w: 4.4, h: 0.44, fontFace: F, fontSize: 24, color: INK2, margin: 0 });

  card(s, 8.30, 5.24, 4.48, 1.20, CARD, LINE);
  s.addText("Gpx3 is our strongest signal.", {
    x: 8.56, y: 5.24, w: 3.96, h: 1.20, fontFace: F, fontSize: T_BODY, bold: true, color: INK, margin: 0, valign: "middle",
  });

  s.addNotes(
`[1:00]  SPEAKER: Pranav

THE HEADLINE
 · 10,546 genes were testable. 146 reach adjusted p below 0.05. 83 up in flight, 63 down.
 · That asymmetry is informative. A fifty-fifty split would suggest noise. An uneven split
   suggests a directional programme.

GPX3 — spend time here
 · Up 1.9-fold at an adjusted p of seven times ten to the minus sixteen. That is the strongest
   signal in the entire dataset by three orders of magnitude, and it sits at a mean of about
   2,000 counts, so it is not a low-count artefact.
 · Gpx3 is glutathione peroxidase 3. It is a secreted, selenium-dependent antioxidant, and in
   the spleen it is made by stromal cells rather than immune cells.
 · It has never been reported in any spaceflight tissue. Remember it — it comes back as the
   centre of Aim 2 and Aim 3.

THE DOWN SIDE, pointing at the left of the plot
 · Rgs13 is a germinal-centre B cell marker.
 · Trim10 is erythroid-specific.
 · Isg15 is one of the classic interferon-stimulated genes.
 · Three different systems, all falling.

HOW WE CHOSE THESE
 · Adjusted p-values only, never raw. With ten thousand tests a one-percent raw rate would
   leave a hundred false positives.
 · No fold-change cut-off, and this is worth explaining. At a two-fold threshold this dataset
   gives you literally zero genes. The real signal is many genes moving a moderate amount
   together, which is what the next slide shows.

CROSS-CHECK
 · GeneLab ran their own analysis on the full gene set. 57 of their 80 significant genes are
   in our 146, and fold changes correlate at 0.86 across 14,400 shared genes.

If asked why 146 and not 80: same data, different filtering. We removed carryover transcripts
and used a per-sample expression filter, which lowers the multiple-testing burden. Every shared
gene agrees in direction and magnitude.`);
}

// ======================================= 5. DATA ANALYSIS: MODULES ==========
{
  const s = slide();
  head(s, "Data Analysis: three coordinated modules");

  const im = fit("figures/fig_three_modules.png", M, 1.24, 6.40, 5.05);
  s.addImage(im);
  caption(s, M, 6.42, 6.40, "Figure 5. Six representative genes per module.", ATTR_PLOT);

  const mods = [
    ["Stromal genes rise", "p = 1.3 × 10⁻⁷", TEAL, TEAL_L],
    ["Erythroid genes fall", "p = 4.9 × 10⁻⁸", RUST, RUST_L],
    ["Interferon genes fall", "p = 4.5 × 10⁻⁸", PLUM, PLUM_L],
  ];
  mods.forEach(([t, stat, c, cl], i) => {
    const y = 1.52 + i * 1.70;
    card(s, 7.30, y, 5.48, 1.36, cl, c);
    s.addText(t, { x: 7.58, y: y + 0.10, w: 5.0, h: 0.52, fontFace: F, fontSize: 27, bold: true, color: c, margin: 0, valign: "middle" });
    s.addText(stat, { x: 7.58, y: y + 0.70, w: 5.0, h: 0.46, fontFace: F, fontSize: 22, color: INK, margin: 0, valign: "middle" });
  });

  s.addNotes(
`[1:00]  SPEAKER: Aryan

INTERPRET THE FIGURE FIRST, out loud
 · A filled dot means that gene is individually significant. An open dot means it moves with
   the module but does not clear the threshold on its own.
 · The dashed line is the module median. The bar is the standard error.
 · Six representative genes are shown per module; the statistics use all of them.

THE THREE MODULES
 · Green, top. Stromal and perivascular genes, all up. Gpx3, Sparcl1, Aebp1, Wt1, Pdgfra and
   Cxcl12 are the fibroblast and vessel-associated genes that build the splenic scaffold.
   Cxcl12 in particular is the chemokine that tells progenitors where to sit. Ten of ten are
   individually significant.
 · Terracotta, middle. Erythroid genes, all down. Gypa is glycophorin A, the red-cell surface
   protein. Ahsp is the alpha-haemoglobin stabilising protein. Trim10 is erythroid-specific.
   Hmbs and Alas2 are enzymes of heme biosynthesis. These are the genes of making red blood
   cells, and the whole set moves in the same direction.
 · Purple, bottom. Type one and type two interferon genes, down. Isg15, Ifit1, Rsad2, Mx1 —
   the standing antiviral programme that keeps a tissue ready for infection.

WHY THIS IS NOT CHERRY-PICKING — the methodological point
 · We did not eyeball three lists. Each module was tested as a set against all 10,546 tested
   genes using a rank-based test, which asks whether the module is unusual FOR THIS DATASET.
 · All three come out below ten to the minus seven. That is the number on the cards.
 · Three converging lines of evidence is exactly what the course asks for, and they corroborate
   rather than repeat each other: one is structural, one is production, one is readiness.

THE READING
 · The scaffold is expanding while blood production and immune readiness fall. A spleen that
   has stopped building.`);
}

// ======================================= 6. DATA ANALYSIS: PATHWAYS =========
{
  const s = slide();
  head(s, "Data Analysis: pathways find the same three signals");

  s.addText("Same three signals, from a completely different method.", {
    x: M, y: 1.08, w: W - 2 * M, h: 0.50, fontFace: F, fontSize: 26, bold: true,
    color: TAUPE, margin: 0, valign: "middle",
  });

  const im = fit("figures/fig_gsea.png", M, 1.72, 11.0, 4.40);
  s.addImage(im);
  caption(s, M, 6.28, 11.0, "Figure 6. GSEA across GO, Hallmark and Reactome.", ATTR_PLOT);

  s.addNotes(
`[0:50]  SPEAKER: Aryan

THE LOGIC OF THIS SLIDE
 · The last slide looked at individual genes. This one throws away the individual gene
   thresholds entirely and scores whole pathways against the ranked list. Completely different
   statistics, same three answers. That is what makes it convincing.

UP IN FLIGHT, in green
 · TGF-beta signalling and response to TGF-beta. TGF-beta is the classic driver of fibroblast
   activation and matrix deposition.
 · Axon guidance. This one always gets a question, so get in front of it: in a non-neural
   tissue those genes are the semaphorins, neuropilins and plexins, and their job in spleen is
   patterning blood vessels, not nerves. We checked the leading edge gene by gene.

DOWN IN FLIGHT
 · Heme metabolism, in terracotta. The leading edge is the entire heme biosynthesis route —
   Alas2, Urod, Cpox, Fech — plus the red-cell membrane skeleton. That is a programme, not a
   gene.
 · Interferon, in purple, showing up in three separate gene sets: interferon signalling,
   interferon alpha response and interferon gamma response. Three independent libraries
   agreeing means it is not one database's quirk.
 · In grey, a fourth signal we did not go looking for: proliferation is down. E2F targets and
   the G2-M checkpoint. Consistent with a tissue that has stopped making new cells.

THE CHECK THAT MATTERS
 · For every pathway we went back to its member genes and confirmed they actually move. A
   pathway is only as good as the fold changes inside it. Our instructors were explicit that
   this is where teams go wrong — picking an attractive pathway name without checking whether
   its genes did anything.
 · Over-representation analysis, run separately with the correct background, agrees: heme
   metabolism comes out 7.7-fold enriched at an adjusted p of 7.3 times ten to the minus four.

Every term on this chart passes both FDR and family-wise error rate below 0.25.`);
}

// ======================================= 7. HYPOTHESIS AND AIMS =============
{
  const s = slide();
  head(s, "Hypothesis and Specific Aims");

  card(s, M, 1.12, W - 2 * M, 0.88, CARD, LINE);
  s.addText("The niche changes first, and the output follows.", {
    x: M + 0.32, y: 1.12, w: W - 2 * M - 0.64, h: 0.88, fontFace: F, fontSize: 27, bold: true,
    color: INK, margin: 0, valign: "middle",
  });

  const im = fit("figures/fig_model.png", M, 2.14, W - 2 * M, 2.90);
  s.addImage(im);
  caption(s, M, 5.10, 11.4, "Figure 7. Our model.", ATTR_TEAM);

  const aims = [
    ["1", "Count progenitors", TEAL],
    ["2", "Find the Gpx3 cell", RUST],
    ["3", "Test selenium", PLUM],
  ];
  aims.forEach(([n, t, c], i) => {
    const x = M + i * 4.15;
    card(s, x, 5.86, 3.85, 0.84, SURFACE, c);
    s.addShape(pres.ShapeType.ellipse, { x: x + 0.22, y: 6.03, w: 0.50, h: 0.50, fill: { color: c }, line: { color: c } });
    s.addText(n, { x: x + 0.22, y: 6.03, w: 0.50, h: 0.50, fontFace: F, fontSize: 22, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0 });
    s.addText(t, { x: x + 0.84, y: 5.86, w: 2.90, h: 0.84, fontFace: F, fontSize: 22, bold: true, color: INK, margin: 0, valign: "middle" });
  });

  s.addNotes(
`[0:50]  SPEAKER: Vedant

THE HYPOTHESIS — state it in full, this is the required wording
 "If spaceflight rebuilds the splenic stromal niche, then flight spleens will make fewer blood
  cells and lose immune organisation, and the stroma will change actively rather than shrink
  with the cells it lost."

 · The word doing the work is ACTIVELY. Everyone already knows the immune cells disappear.
   We are claiming the tissue around them is being rebuilt, not just left behind.
 · That is testable and it is falsifiable. If the stroma were shrinking in proportion to lost
   lymphocytes, our stromal genes would go down, not up. They go up.

WALK THE FIGURE
 · Left, ground control: organised white-pulp zones, active erythropoiesis in the red pulp.
 · Middle: the three signals from our data.
 · Right, after thirty-three days: stroma-dominated, zones blurred.

THE THREE AIMS, and say why each exists
 · Aim 1 asks whether the erythroid loss is even real. Bulk RNA-seq cannot tell "this spleen
   makes fewer red cells" apart from "this spleen has less blood trapped inside it". The only
   way to know is to count cells, in a perfused spleen.
 · Aim 2 takes Gpx3, our strongest signal, and asks which cell actually makes it — because
   right now we have a whole-tissue average, not a cell type.
 · Aim 3 is the one we are most excited about. Gpx3 is selenium-dependent, so you can move it
   with diet. That turns an observation into a countermeasure you could actually test.

AIM INDEPENDENCE — this is graded, be ready for it
 · No aim begins "based on the results of Aim 1". Each has its own hypothesis, its own
   read-out, and its own fallback. If Aim 1 comes back null, Aims 2 and 3 still run.`);
}

// ======================================= 8. METHODOLOGY =====================
{
  const s = slide();
  head(s, "Methodology");

  card(s, M, 1.18, W - 2 * M, 0.88, CARD, LINE);
  s.addText("28 days hindlimb unloading  ·  n = 12 per group  ·  both sexes  ·  C57BL/6J", {
    x: M + 0.32, y: 1.18, w: W - 2 * M - 0.64, h: 0.88, fontFace: F, fontSize: T_BODY, bold: true,
    color: INK, margin: 0, valign: "middle",
  });

  const im = fit("figures/fig_aims_design.png", M, 2.34, W - 2 * M, 3.45);
  s.addImage(im);
  caption(s, M, 5.94, 11.4, "Figure 8. Experimental design for the three aims.", ATTR_TEAM);

  s.addNotes(
`[0:50]  SPEAKER: Vedant

Point at the cards. Do not read them.

THE SHARED PLATFORM
 · Twenty-eight days of hindlimb unloading, against an ambulatory control in the same cage
   with the same handling. Randomised, and scorers blinded to group.
 · Twelve mice per group, both sexes. Both sexes because it is an NIH directive and because
   RR-9 was male-only, which is a real limitation of the dataset we are building on.
 · Sample size from a prospective power analysis at alpha 0.05, using standard deviations from
   published CFU-E and flow cytometry work — not a retrospective calculation after the fact.
 · Spleens perfused before harvest. That single step is what makes Aim 1 answerable, because
   otherwise we would be measuring trapped blood rather than blood production.

AIM 1 — is the erythroid loss real?
 · Ter119 and CD71 flow cytometry to stage the progenitors, so we can see whether they are
   absent or stuck at a particular stage.
 · CFU-E colony assays, which measure functional capacity rather than surface markers.
 · Blinded red-pulp histology. All three normalised per gram of tissue.
 · Fallback: if progenitor number is normal, we test for a maturation arrest instead.

AIM 2 — which cell makes Gpx3?
 · Single-nucleus RNA-seq, because splenic stromal cells are fragile and do not survive
   whole-cell dissociation well.
 · RNAscope to put Gpx3 physically in place in the tissue.
 · Immunofluorescence for B and T zone segregation, to see whether organisation is lost.
 · Fallback: if the zones are intact, we measure composition by deconvolution instead.

AIM 3 — can selenium protect the niche?
 · Selenium-adequate versus selenium-supplemented diet through unloading.
 · Gpx3 activity and oxidative damage as the mechanistic read-out.
 · A poly(I:C) challenge with an ISG time-course, to test whether interferon readiness recovers.
 · Fallback: if diet does not raise activity, we add an AAV Gpx3 arm.

THE PITFALL — say it before you are asked
 · Hindlimb unloading is not microgravity. It works by fluid redistribution, it was built as a
   musculoskeletal model, and it stresses the animals. So we include a restraint-only arm to
   separate the stress-hormone effect from the unloading effect.
 · Splenic erythropoiesis is mouse-specific, so Aim 1 constrains what we can claim for humans.
   We say that rather than over-reaching.`);
}

// ======================================= 9. CONCLUSIONS =====================
{
  const s = slide();
  head(s, "Conclusions and Significance");

  const findings = [
    ["146 genes change", "in three coordinated modules", TEAL, TEAL_L],
    ["Gpx3 is new to spaceflight", "and it is our strongest signal", RUST, RUST_L],
    ["Selenium is a cheap test", "of whether that response helps or harms", PLUM, PLUM_L],
  ];
  findings.forEach(([big, t, c, cl], i) => {
    const y = 1.44 + i * 1.44;
    card(s, M, y, W - 2 * M, 1.22, cl, c);
    s.addText([
      { text: big + "  ", options: { bold: true, color: c } },
      { text: t, options: { color: INK } },
    ], { x: M + 0.36, y, w: W - 2 * M - 0.72, h: 1.22, fontFace: F, fontSize: 27, margin: 0, valign: "middle" });
  });

  s.addText("The same processes run in immune ageing on Earth.", {
    x: M, y: 6.02, w: W - 2 * M, h: 0.56, fontFace: F, fontSize: 26, bold: true,
    color: TAUPE, margin: 0, valign: "middle",
  });

  s.addNotes(
`[0:40]  SPEAKER: Kireeti

 · 146 genes change in the flight spleen, and they fall into three coordinated modules that
   each hold up against a test of the whole transcriptome. Stroma up, blood production down,
   immune readiness down. That is a spleen that has stopped building.
 · Gpx3 is our strongest signal and it has not been reported in any spaceflight tissue before.
   It is also selenium-dependent, which means the countermeasure we propose is a diet rather
   than a drug — cheap, testable, and something you could actually put on a spacecraft.

INNOVATION versus IMPACT, keep them separate
 · Innovation: this is the first analysis of RR-9 spleen on its own, and the first report of
   Gpx3 in spaceflight tissue.
 · Impact: the same niche processes — stromal expansion, falling interferon tone, less
   blood-cell output — are what happens in immune ageing and in chronic stress on Earth. If a
   dietary antioxidant can hold the splenic niche together in an unloaded mouse, that is a lead
   for ageing patients, not only for astronauts.

Do not let this slide get cut. If you reach slide 8 at 6:30, shorten slide 8 and come here.`);
}

// ============================ 10. THANKS, ACKNOWLEDGEMENTS, REFERENCES ======
{
  const s = slide();
  head(s, "Thank you");

  s.addText("Acknowledgements", {
    x: M, y: 1.32, w: 6.2, h: 0.46, fontFace: F, fontSize: 26, bold: true, color: TAUPE, margin: 0,
  });
  s.addText([
    { text: "Analysis notebooks were provided in the Google Colab environment through the GL4HS summer training program.", options: { breakLine: true } },
    { text: " ", options: { breakLine: true, fontSize: 10 } },
    { text: "NASA GeneLab for High Schools · NASA OSDR · the RR-9 investigators · our GL4HS instructors.", options: { breakLine: true } },
    { text: " ", options: { breakLine: true, fontSize: 10 } },
    { text: "Thank you for your time and your interest.", options: { bold: true } },
  ], { x: M, y: 1.90, w: 6.2, h: 4.40, fontFace: F, fontSize: T_BODY, color: INK, margin: 0, valign: "top", lineSpacingMultiple: 1.08 });

  s.addText("Selected References", {
    x: 7.20, y: 1.32, w: 5.58, h: 0.46, fontFace: F, fontSize: 26, bold: true, color: TAUPE, margin: 0,
  });
  const refs = [
    "Gridley DS, et al. Changes in mouse thymus and spleen after return from the STS-135 mission in space. PLoS One. 2013;8(9):e75097.",
    "Mebius RE, Kraal G. Structure and function of the spleen. Nat Rev Immunol. 2005;5(8):606–616.",
    "Inra CN, et al. A perisinusoidal niche for extramedullary haematopoiesis in the spleen. Nature. 2015;527(7579):466–471.",
    "Galazka JM, et al. Transcriptional profiling of spleens from mice flown on the RR-9 mission. NASA OSDR; 2021. doi:10.26030/k030-ms28",
  ];
  s.addText(refs.map((r, i) => ({ text: (i + 1) + ".  " + r, options: { breakLine: i < refs.length - 1 } })), {
    x: 7.20, y: 1.90, w: 5.58, h: 4.40, fontFace: F, fontSize: 16, color: INK2,
    margin: 0, valign: "top", lineSpacingMultiple: 1.12, paraSpaceAfter: 14,
  });

  s.addNotes(
`[0:25]  ALL FOUR SPEAKERS

Kireeti: "Our analysis notebooks came through the GL4HS summer training program in Google
Colab, and the dataset through the NASA Open Science Data Repository and the RR-9 Biospecimen
Sharing Program. Thank you to our instructors and mentors."

Do not flip past the references. Say something like: "Our work rested most heavily on Gridley
and colleagues for what spaceflight does to the spleen, on Mebius and Kraal for how the tissue
is organised, and on Inra and colleagues for the perisinusoidal niche that our whole hypothesis
is built on."

Then: "Thank you for your time and your interest. We're happy to take questions."

HANDLING QUESTIONS
 · Summarise the question before answering. "You asked whether ... I think that ..."
 · Take turns. Do not let one person become the question specialist.
 · It is fine not to know. Use one of these:
     "That was beyond the scope of our research, but we'd be happy to look into it."
     "Could you say a bit more about what you mean? It may not be something we considered."
     "We don't have an answer at the moment, but our guess would be ..."
 · Do not invent an answer.

LIKELY QUESTIONS
 · How do you know it's microgravity and not the cohort difference? We don't, from this
   dataset. That is why every aim proposes a controlled ground analogue.
 · Why hindlimb unloading for a spleen? It is the standard rodent analogue and reproduces the
   fluid shift. We add a restraint-only arm because it also stresses immune tissue.
 · Isn't a 1.9-fold change small? For one gene, yes. Our case rests on many genes moving
   together, which is why we tested the modules as blocks.
 · Why is axon guidance in a spleen? Those genes are semaphorins and neuropilins. GO annotates
   them from neural work, but in spleen they pattern blood vessels.
 · What about the low-depth samples? Five libraries are under 10 million reads. Depth does not
   differ between groups, so it costs power rather than creating a false effect, and we kept
   all 20 to match GeneLab's own analysis.`);
}

pres.writeFile({ fileName: "GL4HS_Capstone_TheSpleenMachine_OSD-420-3.pptx" })
  .then((f) => console.log("wrote", f));
