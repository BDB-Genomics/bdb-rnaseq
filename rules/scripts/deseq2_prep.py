#!/usr/bin/env python3
"""
DESeq2 count matrix preparation script.

Generates:
- Normalized counts (VST or rlog transformed)
- PCA coordinates per sample
- Sample correlation matrix
- Gene-wise dispersion estimates
- List of genes filtered out

Usage:
    snakemake --singularity [...] deseq2_prep
Or run directly:
    python3 rules/scripts/deseq2_prep.py --counts counts.txt --samples samples.tsv --output-dir results/deseq2
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def parse_counts(counts_path: Path) -> pd.DataFrame:
    with counts_path.open("r", encoding="utf-8") as handle:
        first_line = handle.readline()

    if first_line.startswith("Gene"):
        df = pd.read_csv(counts_path, sep="\t", index_col=0)
    else:
        df = pd.read_csv(counts_path, sep="\t", index_col=0, comment="#")

    # Clean the column names (BAM file paths) to match sample names
    # e.g., 'results/markduplicates/sample1.sorted.dup.bam' -> 'sample1'
    new_columns = []
    for col in df.columns:
        base = Path(col).name
        for suffix in [".sorted.dup.bam", ".sorted.bam", ".dup.bam", ".bam"]:
            if base.endswith(suffix):
                base = base[: -len(suffix)]
                break
        new_columns.append(base)
    df.columns = new_columns

    df.index = df.index.astype(str)
    return df


def parse_samples(samples_path: Path) -> pd.DataFrame:
    df = pd.read_csv(samples_path, sep="\t", dtype=str)
    df = df.dropna(subset=["sample", "condition"], how="any")
    df["sample"] = df["sample"].str.strip()
    df["condition"] = df["condition"].str.strip()
    return df


def filter_low_expr_counts(
    counts: pd.DataFrame, min_mean: float
) -> tuple[pd.DataFrame, list[str]]:
    gene_means = counts.mean(axis=1)
    keep_genes = gene_means[gene_means >= min_mean].index.tolist()
    filtered_genes = gene_means[gene_means < min_mean].index.tolist()
    return counts.loc[keep_genes], filtered_genes


def normalize_vst(counts: pd.DataFrame) -> pd.DataFrame:
    counts_arr = counts.values.astype(float)
    log2_counts = np.log2(counts_arr + 1)
    gene_means = log2_counts.mean(axis=1)
    gene_vars = log2_counts.var(axis=1)
    vst_mat = ((log2_counts.T - gene_means) / np.sqrt(gene_vars + 0.1)).T
    vst_df = pd.DataFrame(vst_mat, index=counts.index, columns=counts.columns)
    return vst_df


def rlog_like(counts: pd.DataFrame, alpha: float = 0.1) -> pd.DataFrame:
    size_factors = counts.sum(axis=0)
    normalized = counts.div(size_factors, axis=1) * 1e6
    rlog = np.log2(normalized + alpha)
    return rlog


def compute_pca(normalized: pd.DataFrame, n_top: int = 500) -> pd.DataFrame:
    """Compute PCA on the top variable genes using SVD."""
    top_genes = normalized.var(axis=1).nlargest(n_top).index
    data = normalized.loc[top_genes].T  # (samples, genes)
    data = data.fillna(0)
    centered = data.values - data.values.mean(axis=0)
    U, S, Vt = np.linalg.svd(centered, full_matrices=False)
    pc_coords = U[:, :2] * S[:2]
    pca_df = pd.DataFrame(
        {"PC1": pc_coords[:, 0], "PC2": pc_coords[:, 1]}, index=data.index
    )
    return pca_df


def compute_correlation(normalized: pd.DataFrame) -> pd.DataFrame:
    corr = normalized.T.corr()
    return corr


def write_dispersions(counts: pd.DataFrame, output_path: Path) -> None:
    counts_arr = counts.values.astype(float)
    gene_means = counts_arr.mean(axis=1)
    gene_vars = counts_arr.var(axis=1)
    dispersions = gene_vars / (gene_means + 0.1)
    disp_df = pd.DataFrame(
        {"mean": gene_means, "dispersion": dispersions}, index=counts.index
    )
    disp_df.to_csv(output_path, sep="\t", index=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="DESeq2 count matrix preparation")
    parser.add_argument(
        "--counts", required=True, type=Path, help="Path to raw counts.txt"
    )
    parser.add_argument(
        "--samples", required=True, type=Path, help="Path to samples.tsv"
    )
    parser.add_argument(
        "--output-dir", required=True, type=Path, help="Output directory"
    )
    parser.add_argument(
        "--min-mean-expr", type=float, default=1, help="Minimum mean expression"
    )
    parser.add_argument(
        "--padj-threshold", type=float, default=0.05, help="Adjusted p-value threshold"
    )
    args = parser.parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    sys.stderr.write(f"[DESEQ2_PREP] Loading counts from {args.counts}\n")
    counts = parse_counts(args.counts)

    sys.stderr.write(f"[DESEQ2_PREP] Loading sample metadata from {args.samples}\n")
    samples_meta = parse_samples(args.samples)

    common_samples = [s for s in samples_meta["sample"] if s in counts.columns]
    if not common_samples:
        sys.stderr.write(
            "[DESEQ2_PREP ERROR] No sample names match between counts and sample sheet\n"
        )
        sys.exit(1)

    counts = counts[common_samples]
    samples_meta = samples_meta[samples_meta["sample"].isin(common_samples)]

    sys.stderr.write(
        f"[DESEQ2_PREP] Filtering low-expressed genes (min_mean={args.min_mean_expr})\n"
    )
    counts_filt, filtered_genes = filter_low_expr_counts(counts, args.min_mean_expr)

    sys.stderr.write("[DESEQ2_PREP] Normalizing counts (VST-like)\n")
    normalized = normalize_vst(counts_filt)

    sys.stderr.write("[DESEQ2_PREP] Computing PCA\n")
    pca_df = compute_pca(normalized)

    sys.stderr.write("[DESEQ2_PREP] Computing sample correlation\n")
    corr_df = compute_correlation(normalized)

    sys.stderr.write("[DESEQ2_PREP] Writing outputs\n")

    normalized.to_csv(output_dir / "normalized_counts.txt", sep="\t", index=True)
    pca_df.to_csv(output_dir / "pca.txt", sep="\t", index=True)
    corr_df.to_csv(output_dir / "sample_correlation.txt", sep="\t", index=True)

    write_dispersions(counts_filt, output_dir / "dispersions.txt")

    with (output_dir / "genes_filtered.txt").open("w", encoding="utf-8") as f:
        f.write("gene_id\n")
        for g in filtered_genes:
            f.write(f"{g}\n")

    sys.stderr.write(f"[DESEQ2_PREP] Done. Outputs in {output_dir}\n")
    sys.stderr.write(f"[DESEQ2_PREP] Samples used: {', '.join(common_samples)}\n")
    sys.stderr.write(f"[DESEQ2_PREP] Genes filtered: {len(filtered_genes)}\n")
    sys.stderr.write(f"[DESEQ2_PREP] Genes retained: {len(counts_filt)}\n")


if __name__ == "__main__":
    main()
