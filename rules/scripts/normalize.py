#!/usr/bin/env python3
"""
Calculate TPM and FPKM normalized matrices from featureCounts output.
"""

import argparse
import sys
from pathlib import Path
import pandas as pd

def parse_args():
    parser = argparse.ArgumentParser(description="Calculate TPM and FPKM matrices.")
    parser.add_argument("--counts", required=True, type=Path, help="Path to featureCounts output counts.txt")
    parser.add_argument("--tpm", required=True, type=Path, help="Output path for TPM matrix (TSV)")
    parser.add_argument("--fpkm", required=True, type=Path, help="Output path for FPKM matrix (TSV)")
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Read featureCounts table
    with args.counts.open("r", encoding="utf-8") as handle:
        first_line = handle.readline()

    if first_line.startswith("Gene"):
        df = pd.read_csv(args.counts, sep="\t", index_col=0)
    else:
        df = pd.read_csv(args.counts, sep="\t", index_col=0, comment="#")

    if "Length" not in df.columns:
        print("Error: 'Length' column not found in counts file.", file=sys.stderr)
        sys.exit(1)

    gene_lengths = df["Length"].astype(float)

    # Exclude metadata columns
    metadata_cols = ["Chr", "Start", "End", "Strand", "Length"]
    count_cols = [col for col in df.columns if col not in metadata_cols]
    counts_df = df[count_cols].astype(float)

    # Clean the column names (BAM file paths) to match sample names
    new_columns = []
    for col in counts_df.columns:
        base = Path(col).name
        for suffix in [".sorted.dup.bam", ".sorted.bam", ".dup.bam", ".bam"]:
            if base.endswith(suffix):
                base = base[: -len(suffix)]
                break
        new_columns.append(base)
    counts_df.columns = new_columns

    # 1. Compute FPKM
    # library sizes (sum of read counts per sample)
    lib_sizes = counts_df.sum(axis=0)
    # Ensure no division by zero
    lib_sizes = lib_sizes.replace(0, 1)
    gene_lengths = gene_lengths.replace(0, 1)

    # RPM = Counts / (Library size in millions)
    rpm = counts_df.div(lib_sizes, axis=1) * 1e6
    # FPKM = RPM / (Gene length in kilobases)
    fpkm = rpm.div(gene_lengths / 1e3, axis=0)

    # 2. Compute TPM
    # RPK = Counts / (Gene length in kilobases)
    rpk = counts_df.div(gene_lengths / 1e3, axis=0)
    # Sum of RPK per sample
    rpk_sums = rpk.sum(axis=0)
    rpk_sums = rpk_sums.replace(0, 1)
    # TPM = (RPK / Sum of RPK per sample) * 1e6
    tpm = rpk.div(rpk_sums, axis=1) * 1e6

    # Create parent dirs if they don't exist
    args.tpm.parent.mkdir(parents=True, exist_ok=True)
    args.fpkm.parent.mkdir(parents=True, exist_ok=True)

    # Save to TSV
    tpm.to_csv(args.tpm, sep="\t")
    fpkm.to_csv(args.fpkm, sep="\t")
    print(f"Successfully wrote TPM to {args.tpm} and FPKM to {args.fpkm}")

if __name__ == "__main__":
    main()
