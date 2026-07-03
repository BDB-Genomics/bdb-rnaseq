# Pipeline Rules (`.smk`)

This directory contains the modular Snakemake rule definitions that make up the RNA-seq pipeline. Each `.smk` file encapsulates a specific bioinformatics tool or process, keeping the main `Snakefile` clean and maintainable.

---

## 🏗️ Architecture

The rules are designed to be entirely modular and self-contained. Every rule specifies its own:
- **Inputs and Outputs**: Dynamically resolved via `config.yaml`.
- **Resources**: Memory and time constraints for HPC scheduling.
- **Environment**: Tool-specific Conda definitions (found in `envs/`).
- **Telemetry**: Distinct log and benchmark outputs.

---

## 📁 Rule Categories

### 1. Preprocessing & Quality Control
| Rule File | Purpose |
|---|---|
| `fastp.smk` | Adapters trimming, quality filtering, and read truncation. |
| `fastqc.smk` | Raw read quality metrics generation. |
| `preseq.smk` | Library complexity estimation. |
| `qc_gate.smk` | Automated threshold validation (mapping rates, duplicates, reads). Flags samples as PASS/FAIL. |
| `multiqc.smk` | Aggregation of all QC logs into a single HTML report. |

### 2. Alignment & Processing
| Rule File | Purpose |
|---|---|
| `star.smk` | Spliced-aware alignment of reads to the reference genome. |
| `markduplicates.smk` | Picard-based PCR duplicate marking and read sorting. |
| `samtools_sort.smk` | BAM coordinate sorting. |
| `samtools_index.smk` | BAM indexing (.bai) for fast random access. |
| `samtools_stats.smk` | Comprehensive BAM alignment statistics computation. |

### 3. Quantification & Analytics
| Rule File | Purpose |
|---|---|
| `featurecounts.smk` | Transcript/gene-level read summarization and raw count matrix generation. |
| `rseqc.smk` | RNA-seq specific QC (read distribution, gene body coverage, infer experiment). |
| `deseq2_prep.smk` | Count matrix normalization (VST), dispersion estimation, and PCA processing. |

---

## 🔒 Best Practices Implemented

1. **Strict Error Handling**: All shell directives use `set -euo pipefail` to ensure tools fail fast on hidden errors.
2. **Deterministic Environments**: Every rule relies on a pinned Conda environment from `envs/`.
3. **Robust Templating**: Paths are never hardcoded; they are universally referenced from `config.yaml`.
4. **Log Redirection**: All `stderr` (`2>`) and `stdout` (`>`) are captured into rule-specific log files for telemetry parsing.
