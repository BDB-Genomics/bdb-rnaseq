<p align="center">
  <img src="assets/pipeline_diagram.svg" alt="Pipeline DAG" width="800" />
</p>

# BDB-Genomics RNA-seq Pipeline

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://github.com/BDB-Genomics/RNAseq-pipeline/actions"><img src="https://img.shields.io/badge/Status-Integration_Testing-orange" alt="Status"></a>
  <a href="https://snakemake.readthedocs.io"><img src="https://img.shields.io/badge/Snakemake-≥7.0-brightgreen.svg" alt="Snakemake"></a>
</p>

<p align="center">
  <img src="assets/readme_animation.svg" alt="RNA-seq Pipeline Overview" width="820" />
</p>

> A modular, industry-standard Snakemake workflow for paired-end bulk RNA-seq processing — from raw FASTQ files to quantified gene expression, QC gating, and comprehensive reporting.

## Status

- Fully resolved DAG with validated I/O contracts
- 4 new rules added: markduplicates, rseqc, preseq, deseq2_prep
- Ready for integration testing and iteration toward industry-standard parity

## Repository Layout

```
.
├── Snakefile                 # Main Snakemake entry point
├── config.yaml               # Central configuration (all rules)
├── rules/
│   ├── *.smk                # Modular rule files
│   ├── envs/                 # Per-rule Conda environments
│   └── scripts/              # Helper scripts (validate_config.py, etc.)
├── profiles/
│   ├── local/               # Local execution profile
│   └── slurm/                # SLURM cluster profile
├── scripts/
│   ├── run_pipeline.sh      # Wrapper script for execution
│   └── directory_structure.sh # Create expected directory layout
└── data/
    └── fastp/samples.tsv     # Sample sheet
```

## Inputs

The pipeline expects:

- `config.yaml` — Central configuration file
- `data/fastp/samples.tsv` — Sample sheet with FASTQ paths and metadata
- Reference files — STAR genome index, GTF annotation, RSeQC refGene BED (configure in `config.yaml`)

### Sample Sheet Format

`data/fastp/samples.tsv` must contain:

| Column | Description |
|--------|-------------|
| `sample` | Unique sample identifier |
| `fastq_r1` | Path to R1 FASTQ |
| `fastq_r2` | Path to R2 FASTQ |
| `replicate` | Replicate number (positive integer) |
| `condition` | Experimental condition |

Optional: `control` — path to control sample or `NONE`

Example:

```tsv
sample	fastq_r1	fastq_r2	replicate	condition
sample1	data/fastq/sample1_R1.fastq.gz	data/fastq/sample1_R2.fastq.gz	1	control
sample2	data/fastq/sample2_R1.fastq.gz	data/fastq/sample2_R2.fastq.gz	1	treatment
```

## Quick Start

### 1. Configure

Edit `config.yaml` and set:

```yaml
global:
  samples: "data/fastp/samples.tsv"
  index: "/path/to/star/index"        # Generate with STAR --runMode genomeGenerate
  gtf: "/path/to/annotation.gtf"      # GTF annotation file
  refgene: "/path/to/refgene.bed"     # RSeQC reference gene BED

star:
  params:
    index: "/path/to/star/index"
    sjdbOverhang: 100                  # Read length - 1
```

### 2. Dry Run

```bash
scripts/run_pipeline.sh --dry-run
```

### 3. Run

```bash
scripts/run_pipeline.sh --cores 8
```

### 4. SLURM Cluster

```bash
snakemake --profile profiles/slurm --configfile config.yaml
```

## Configuration

`config.yaml` is organized by rule. Key sections:

| Section | Purpose |
|---------|---------|
| `global` | Samples, references (STAR index, GTF, refGene) |
| `fastp` | Trimming parameters |
| `fastqc` | Post-trim QC |
| `star` | Splice-aware alignment |
| `samtools_sort` | BAM sorting |
| `markduplicates` | PCR duplicate marking |
| `samtools_index` | BAM indexing |
| `samtools_stats` | Alignment statistics |
| `rseqc` | RNA-seq QC metrics |
| `preseq` | Library complexity estimation |
| `featurecounts` | Gene quantification |
| `deseq2_prep` | Normalized counts, PCA, correlation |
| `qc_gate` | Threshold-based QC filtering |
| `multiqc` | Aggregate QC reporting |

## Outputs

| Directory | Contents |
|-----------|----------|
| `results/fastp/` | Trimmed FASTQs, JSON/HTML reports |
| `results/fastqc/` | FastQC HTML/ZIP reports |
| `results/star/` | Aligned BAMs, alignment logs |
| `results/markduplicates/` | Dup-marked BAMs, metrics |
| `results/samtools_index/` | BAM indices |
| `results/samtools_stats/` | Alignment statistics |
| `results/rseqc/` | Gene body coverage, strand inference, read distribution |
| `results/preseq/` | Library complexity curves |
| `results/featurecounts/` | Raw counts matrix |
| `results/deseq2/` | VST-normalized counts, PCA, correlation |
| `results/qc_gate/` | QC pass/fail per sample |
| `results/multiqc/` | Aggregated QC report |

## Requirements

- Snakemake ≥7.0
- Conda (for `--use-conda`)
- Python ≥3.9
- Reference files (STAR index, GTF, refGene BED)

## License

See [LICENSE](LICENSE).

---

Built by [BDB-Genomics](https://github.com/bdb-genomics) — advancing discoveries through modular, industry-standard computational tools.