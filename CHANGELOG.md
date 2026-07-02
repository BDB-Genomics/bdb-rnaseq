# Changelog

Notable changes to the BDB-Genomics RNA-seq Pipeline are recorded here.

## [Unreleased]

## [v1.1.0] - 2026-07-03

### Added
- Added `test_envs.sh` script to dynamically validate all 12 Conda/Mamba environments with automatic exit cleanup.

### Fixed
- Relocated Java options configuration in `rules/markduplicates.smk` to execute Picard MarkDuplicates correctly.

### Removed
- Removed obsolete matplotlib visualization scripts (`scripts/generate_flowchart.py`, `scripts/generate_dag.py`) and static image assets (`pipeline_flowchart.png`, `pipeline_dag.dot`).
- Removed unused local workspace configuration (`rules/atacseq.code-workspace`).

## [v1.0.0] - 2026-04-17

Initial release of the modular RNA-seq Pipeline — a production-grade, industry-standard Snakemake workflow for paired-end bulk RNA-seq processing.

### Core Pipeline

- **Preprocessing**: fastp (adapter trimming, quality filtering), FastQC (quality assessment)
- **Alignment**: STAR (splice-aware, supports ~50bp-200bp reads)
- **Post-alignment**: samtools sort, markduplicates (Picard), samtools index, samtools stats
- **QC**: RSeQC (gene body coverage, strand inference, read distribution), Preseq (library complexity)
- **Quantification**: featureCounts (gene-level, stranded, supports paired-end)
- **Downstream**: DESeq2-ready normalized counts, PCA, sample correlation
- **Reporting**: QC gate (threshold-based filtering), MultiQC aggregation

### Design Features

- **Modular architecture** — Each tool is a self-contained rule with isolated Conda environment
- **Reproducible** — Conda + Singularity containerization, per-rule versions pinned
- **Production-ready** — Config validation, resource management (mem/threads/time), SLURM/local profiles
- **Extensible** — Add advanced integrations without modifying core pipeline
- **I/O consistency** — Dup-marked BAMs flow through all downstream tools

### Pipeline Structure

```
FASTQ → fastp → fastqc → STAR → samtools_sort → markduplicates
                                                      ↓
                        samtools_index ←────────────────┘
                              ↓
                        samtools_stats → rseqc → preseq
                              ↓
                        featurecounts → deseq2_prep
                              ↓
                           multiqc
```

### New Rules Added

| Rule | Tool | Purpose |
|------|------|---------|
| `markduplicates` | Picard MarkDuplicates | PCR duplicate marking |
| `rseqc` (4 rules) | RSeQC | Gene body coverage, strand inference, read distribution, bam stat |
| `preseq` | Preseq | Library complexity estimation |
| `deseq2_prep` | Python script | VST normalization, PCA, sample correlation |

### Known Issues

- `validate_config.py` has PATH_CHECKS referencing incorrect config keys (to be fixed)
- Scripts assume RNA-seq context (ATAC-seq references removed)

### Coming Soon

- Differential expression analysis (DESeq2/edgeR)
- Fusion detection (STAR-Fusion/Arriba)
- Complex heatmaps, pathway enrichment
- Formal test suite (unit + integration)
- CI/CD pipeline