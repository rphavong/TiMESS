---
platform: multi
doc_type: comparison
title: "9. Key Cross-Platform Comparisons (→ docs_staging/comparisons/)"
source: TiMESS FAS Platform Guide (curated by Claude, Aug 2026)
---

## 9. Key Cross-Platform Comparisons (→ docs_staging/comparisons/)

**Flex vs. Universal 3'/5' — the fixation trade-off.** Flex trades poly-A capture (species
agnostic, whole transcriptome) for probe-based detection (human/mouse only, protein-coding
focus) in exchange for FFPE/archival compatibility and superior recovery of fragile cell
types. Independent benchmarking backs the sensitivity claim for fixed tissue specifically —
Flex was more sensitive than standard 3'/5' in frozen tumor and FFPE biopsies [4], and
scored best overall in a 9-kit PBMC benchmark [5]. It is not a strict upgrade — species
flexibility is the cost.

**Universal 3' vs. 5' — pick by downstream readout, not by "which is better."** Both share
the same throughput tiers and reverse-transcription chemistry. The deciding factor is
almost always the multiomic add-on: need TCR/BCR or antigen specificity → 5'. Gene
expression only, or protein/ATAC without immune repertoire → 3' [6][9].

**Visium HD vs. Xenium — resolution mechanism differs, not just resolution number.**
Visium HD achieves "single-cell-scale" resolution via dense sequencing-based binning
(8 µm bins approximate but don't guarantee single-cell boundaries); Xenium achieves true
single-cell resolution via imaging and segmentation. Visium HD stays whole-transcriptome;
Xenium is panel-limited (v1) or high-plex-but-still-targeted (Prime). Independent
benchmarking confirms Visium HD's spatial fidelity advantage among sequencing-based
platforms [19], while Xenium's imaging-based approach separately benchmarks ahead of other
imaging platforms (CosMx, MERSCOPE) on sensitivity/specificity [28][29]. For discovery
work where the panel isn't known yet, Visium HD; once genes of interest are defined and
subcellular resolution matters, Xenium.

**Xenium v1 vs. Xenium Prime — panel breadth vs. validated depth.** Prime's 5K panel and
CG000775's own data show higher transcript density than v1's narrower panels, but v1's
248–480-gene curated panels remain more tightly validated for specific tissue/disease
contexts (e.g., Mouse Brain, Human Skin) with tissue-specific cell-type coverage baked in.
Reagents are not cross-compatible — this is a genuine either/or decision at ordering time,
not a simple "upgrade" [27][31][32].

**Visium CytAssist Protein vs. Xenium Protein — where the protein panel lives.** CytAssist
pairs a 35-plex antibody panel with **whole-transcriptome** spatial RNA on FFPE [12][13].
Xenium Protein pairs modular antibody subpanels with a **targeted gene panel** (≤480 genes)
at subcellular resolution [25][26]. Choose CytAssist Protein when whole-transcriptome
breadth is non-negotiable; choose Xenium Protein when subcellular co-localization of RNA
and protein is the priority.

**External literature reviews worth ingesting in full for this folder:**
- 10x Genomics' own literature review of third-party analysis tools spanning Visium and
  Xenium: https://www.10xgenomics.com/analysis-guides/spatial-gex-lit-review
- Official "compare and contrast Visium and Xenium" platform hub: https://www.10xgenomics.com/platforms/visium/product-family
