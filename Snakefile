#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>              Modular RNA-seq Pipeline                                                                         #>
#>              Author: Himanshu Bhandary
#>              Mail: 2032ushimanshu@gmail.com
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

import csv
import os
import subprocess
import tempfile
import yaml
from pathlib import Path

# Load config defaults
configfile: "config.yaml"

# Validate the actual, merged configuration (which includes profile/CLI overrides)
tmp_config_fd, tmp_config_path = tempfile.mkstemp(dir=".", suffix="_merged_config.yaml")
try:
    with os.fdopen(tmp_config_fd, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    
    subprocess.run(
        ["python3", "rules/scripts/validate_config.py", tmp_config_path],
        check=True,
    )
finally:
    if os.path.exists(tmp_config_path):
        os.remove(tmp_config_path)

SAMPLES_TSV = Path(config["global"]["samples"])
with SAMPLES_TSV.open(newline="") as handle:
    rows = list(csv.DictReader(handle, delimiter="\t"))

SAMPLES = [row["sample"] for row in rows]
FASTQ_R1 = {row["sample"]: row["fastq_r1"] for row in rows}
FASTQ_R2 = {row["sample"]: row["fastq_r2"] for row in rows}

if not SAMPLES:
    raise ValueError(f"No samples found in sample sheet: {SAMPLES_TSV}")


# --- Includes ------------------------------------------------------------------
include: "rules/utils.smk"
include: "rules/fastp.smk"
include: "rules/fastqc.smk"

# Alignment
include: "rules/star.smk"

# Post-alignment
include: "rules/samtools_sort.smk"
include: "rules/markduplicates.smk"
include: "rules/samtools_index.smk"
include: "rules/samtools_stats.smk"

# Post-alignment QC
include: "rules/rseqc.smk"
include: "rules/preseq.smk"

# Quantification
include: "rules/featurecounts.smk"
include: "rules/normalize.smk"

# Downstream Analysis
include: "rules/deseq2_prep.smk"

# QC & Reporting
include: "rules/qc_gate.smk"
include: "rules/multiqc.smk"


# --- Targets -------------------------------------------------------------------

PREPROCESSING_TARGETS = [
    expand("results/fastp/{sample}_R1_trimmed.fastq.gz", sample=SAMPLES),
    expand("results/fastqc/{sample}_R1_trimmed_fastqc.html", sample=SAMPLES)
]

ALIGNMENT_TARGETS = [
    expand(f"{config['star']['output']['dir']}/{{sample}}Aligned.out.bam", sample=SAMPLES),
    expand(f"{config['samtools_sort']['output']['sorted_bam']}/{{sample}}.sorted.bam", sample=SAMPLES)
]

MARKDUPLICATES_TARGETS = [
    expand(f"{config['markduplicates']['output']['dir']}/{{sample}}.sorted.dup.bam", sample=SAMPLES),
    expand(f"{config['markduplicates']['output']['dir']}/{{sample}}.dup_metrics.txt", sample=SAMPLES)
]

POSTALIGN_TARGETS = [
    expand(f"{config['samtools_index']['output']['index']}/{{sample}}.sorted.dup.bam.bai", sample=SAMPLES),
    expand(f"{config['samtools_stats']['output']['stats']}/{{sample}}_postFiltering.stats.txt", sample=SAMPLES)
]

RSEQC_TARGETS = [
    expand(f"{config['rseqc']['output']['dir']}/{{sample}}.infer_experiment.txt", sample=SAMPLES),
    expand(f"{config['rseqc']['output']['dir']}/{{sample}}.read_distribution.txt", sample=SAMPLES),
    expand(f"{config['rseqc']['output']['dir']}/{{sample}}.bam_stat.txt", sample=SAMPLES),
    expand(f"{config['rseqc']['output']['dir']}/{{sample}}.geneBodyCoverage.txt", sample=SAMPLES)
]

PRESEQ_TARGETS = []
if not config.get("ci_mode", False):
    PRESEQ_TARGETS = [
        expand(f"{config['preseq']['output']['dir']}/{{sample}}.ccurve.txt", sample=SAMPLES)
    ]

QUANTIFICATION_TARGETS = [
    f"{config['featurecounts']['output']['dir']}/counts.txt",
    config['normalize']['output']['tpm'],
    config['normalize']['output']['fpkm']
]

DESEQ2_TARGETS = [
    f"{config['deseq2_prep']['output']['dir']}/normalized_counts.txt",
    f"{config['deseq2_prep']['output']['dir']}/pca.txt",
    f"{config['deseq2_prep']['output']['dir']}/sample_correlation.txt"
]

QC_GATE_TARGETS = [
    expand("results/qc_gate/{sample}_qc_pass.txt", sample=SAMPLES)
]

REPORT_TARGETS = [
    "results/multiqc"
]


rule all:
    input:
        PREPROCESSING_TARGETS,
        ALIGNMENT_TARGETS,
        MARKDUPLICATES_TARGETS,
        POSTALIGN_TARGETS,
        RSEQC_TARGETS,
        PRESEQ_TARGETS,
        QUANTIFICATION_TARGETS,
        DESEQ2_TARGETS,
        QC_GATE_TARGETS,
        REPORT_TARGETS

onstart:
    print(f"\n[START] BDB-Genomics RNA-seq Pipeline")
    print(f"Samples: {len(SAMPLES)} samples detected\n")

onsuccess:
    print(f"\n[SUCCESS] Pipeline completed successfully!")
    subprocess.run(["python3", "rules/scripts/aggregate_logs.py", "success"])

onerror:
    print(f"\n[ERROR] Pipeline encountered an error.")
    subprocess.run(["python3", "rules/scripts/aggregate_logs.py", "error"])