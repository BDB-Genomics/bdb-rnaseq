#!/usr/bin/env python3
"""Generate synthetic test data for RNA-seq CI pipeline validation.

This script produces a minimal synthetic dataset to ensure all RNA-seq
rules — including STAR alignment, Picard MarkDuplicates, featureCounts,
RSeQC, preseq, and DESeq2 prep — execute successfully in CI.
"""

from __future__ import annotations

import gzip
import os
import pathlib
import random
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Any, IO

# Genome layout
GENOME = {
    "chr1": 400_000,
    "chr2": 200_000,
}

# Annotation parameters
GENES_CHR1 = 40
GENES_CHR2 = 20
GENE_LENGTH = 3000
GENE_START_OFFSET = 5000

# FASTQ parameters
READS_PER_SAMPLE = 5000
READ_LENGTH = 75
FRAGMENT_MEAN = 180
FRAGMENT_SD = 25
SAMPLES = {
    "sample1": {"condition": "Control", "replicate": 1},
    "sample2": {"condition": "Control", "replicate": 2},
    "sample3": {"condition": "Treatment", "replicate": 1},
    "sample4": {"condition": "Treatment", "replicate": 2},
}


@dataclass
class ReferenceData:
    genome_seqs: dict[str, str]
    genes: list[dict[str, Any]]
    transcripts: dict[str, str]  # gene_id -> transcript DNA sequence


def reverse_complement(seq: str) -> str:
    """Returns the reverse complement of a DNA sequence."""
    table = str.maketrans("ACGTNacgtn", "TGCANtgcan")
    return seq.translate(table)[::-1]


def random_seq(length: int) -> str:
    """Generates a random DNA string of the specified length."""
    return "".join(random.choices("ACGT", k=length))


def generate_genome(filepath: str, genome_dict: dict[str, int]) -> dict[str, str]:
    sequences = {}
    offset = 0
    with open(filepath, "w") as fh, open(filepath + ".fai", "w") as fai:
        for chrom, size in genome_dict.items():
            seq = random_seq(size)
            sequences[chrom] = seq
            header = f">{chrom}\n"
            fh.write(header)
            offset += len(header)
            fai.write(f"{chrom}\t{size}\t{offset}\t80\t81\n")
            for i in range(0, len(seq), 80):
                chunk = seq[i : i + 80] + "\n"
                fh.write(chunk)
                offset += len(chunk)
    return sequences


def generate_chrom_sizes(filepath: str) -> None:
    with open(filepath, "w") as fh:
        for chrom, size in GENOME.items():
            fh.write(f"{chrom}\t{size}\n")


def _make_genes(chrom: str, n_genes: int, chrom_size: int) -> list[dict[str, Any]]:
    genes = []
    spacing = (chrom_size - (GENE_START_OFFSET * 2)) // max(1, n_genes)

    for i in range(n_genes):
        start = GENE_START_OFFSET + i * spacing
        end = start + GENE_LENGTH
        if end >= chrom_size - 1000:
            print(
                f"ERROR: Cannot fit {n_genes} genes on {chrom}.",
                file=sys.stderr,
            )
            sys.exit(1)
        strand = "+" if i % 2 == 0 else "-"
        gene_id = f"{chrom.upper()}_GENE{i + 1:03d}"
        genes.append(
            dict(chrom=chrom, start=start, end=end, strand=strand, gene_id=gene_id)
        )
    return genes


def generate_annotation(filepath: str) -> list[dict[str, Any]]:
    all_genes = []
    all_genes += _make_genes("chr1", GENES_CHR1, GENOME["chr1"])
    all_genes += _make_genes("chr2", GENES_CHR2, GENOME["chr2"])
    
    with open(filepath, "w") as fh:
        for g in all_genes:
            c, s, e, st, gid = (
                g["chrom"],
                g["start"],
                g["end"],
                g["strand"],
                g["gene_id"],
            )
            tx_id = f"TX_{gid}"
            fh.write(
                f'{c}\ttest\tgene\t{s}\t{e}\t.\t{st}\t.\tgene_id "{gid}"; gene_name "{gid}";\n'
            )
            fh.write(
                f'{c}\ttest\ttranscript\t{s}\t{e}\t.\t{st}\t.\tgene_id "{gid}"; transcript_id "{tx_id}";\n'
            )
            fh.write(
                f'{c}\ttest\texon\t{s}\t{s + 1000}\t.\t{st}\t.\tgene_id "{gid}"; transcript_id "{tx_id}";\n'
            )
            fh.write(
                f'{c}\ttest\texon\t{e - 1000}\t{e}\t.\t{st}\t.\tgene_id "{gid}"; transcript_id "{tx_id}";\n'
            )
    return all_genes


def generate_refgene_bed(filepath: str, genes: list[dict[str, Any]]) -> None:
    with open(filepath, "w") as fh:
        for g in genes:
            c, s, e, st, gid = (
                g["chrom"],
                g["start"],
                g["end"],
                g["strand"],
                g["gene_id"],
            )
            tx_id = f"TX_{gid}"
            # BED12 columns:
            # 1. chrom, 2. chromStart, 3. chromEnd, 4. name, 5. score, 6. strand
            # 7. thickStart, 8. thickEnd, 9. itemRgb, 10. blockCount, 11. blockSizes, 12. blockStarts
            fh.write(
                f"{c}\t{s}\t{e}\t{tx_id}\t0\t{st}\t{s}\t{e}\t0\t2\t1000,1000\t0,2000\n"
            )


def extract_transcripts(ref_seqs: dict[str, str], genes: list[dict[str, Any]]) -> dict[str, str]:
    transcripts = {}
    for g in genes:
        chrom = g["chrom"]
        seq = ref_seqs[chrom]
        s = g["start"]
        e = g["end"]
        # Splice exon 1 and exon 2
        exon1 = seq[s : s + 1000]
        exon2 = seq[e - 1000 : e]
        tx_seq = exon1 + exon2
        if g["strand"] == "-":
            tx_seq = reverse_complement(tx_seq)
        transcripts[g["gene_id"]] = tx_seq
    return transcripts


def generate_fastq_paired(
    r1_path: str,
    r2_path: str,
    ref: ReferenceData,
    n_reads: int = READS_PER_SAMPLE,
) -> None:
    quals = "I" * READ_LENGTH
    with gzip.open(r1_path, "wt") as f1, gzip.open(r2_path, "wt") as f2:
        read_idx = 0
        gene_ids = list(ref.transcripts.keys())
        
        while read_idx < n_reads:
            gene_id = random.choice(gene_ids)
            tx_seq = ref.transcripts[gene_id]
            
            frag_len = max(
                READ_LENGTH + 10,
                min(int(random.gauss(FRAGMENT_MEAN, FRAGMENT_SD)), len(tx_seq)),
            )
            
            if len(tx_seq) <= frag_len:
                continue
                
            pos = random.randint(0, len(tx_seq) - frag_len)
            fragment = tx_seq[pos : pos + frag_len]
            
            f1.write(f"@READ{read_idx:06d}/1\n{fragment[:READ_LENGTH]}\n+\n{quals}\n")
            f2.write(
                f"@READ{read_idx:06d}/2\n{reverse_complement(fragment[-READ_LENGTH:])}\n+\n{quals}\n"
            )
            read_idx += 1


def generate_star_index(index_dir: str, fasta: str, gtf: str) -> None:
    os.makedirs(index_dir, exist_ok=True)
    star_path = shutil.which("STAR")
    if not star_path:
        print("  STAR executable not found on system PATH. Skipping index building.")
        return
    try:
        subprocess.run(
            [
                star_path,
                "--runMode",
                "genomeGenerate",
                "--genomeDir",
                index_dir,
                "--genomeFastaFiles",
                fasta,
                "--sjdbGTFfile",
                gtf,
                "--genomeSAindexNbases",
                "9",
                "--genomeChrBinNbits",
                "12",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("  STAR genome index built successfully.")
    except Exception as e:
        print(f"WARNING: STAR genomeGenerate failed: {e}", file=sys.stderr)


def generate_samples_tsv(filepath: str, root_dir: pathlib.Path) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as fh:
        fh.write("sample\tfastq_r1\tfastq_r2\treplicate\tcondition\n")
        for sample, info in SAMPLES.items():
            r1 = root_dir / f"data/fastq/{sample}_R1.fastq.gz"
            r2 = root_dir / f"data/fastq/{sample}_R2.fastq.gz"
            fh.write(
                f"{sample}\t{r1}\t{r2}\t{info['replicate']}\t{info['condition']}\n"
            )


def main() -> None:
    random.seed(42)
    root = pathlib.Path(__file__).resolve().parents[2]
    print("=" * 60)
    print("Generating synthetic CI test data for RNA-seq")
    print("=" * 60)
    
    for subdir in [
        "data/fastq",
        "data/reference/star_index",
        "data/fastp",
    ]:
        os.makedirs(os.path.join(root, subdir), exist_ok=True)

    genome_fa = os.path.join(root, "data/reference/genome.fa")
    annotation_gtf = os.path.join(root, "data/reference/annotation.gtf")
    refgene_bed = os.path.join(root, "data/reference/refgene.bed")

    print("\n[1/6] Reference genomes ...")
    genome_seqs = generate_genome(genome_fa, GENOME)
    print(f"  Target genome size: {sum(len(s) for s in genome_seqs.values()):,} bp")

    print("[2/6] Chromosome sizes & Annotation ...")
    generate_chrom_sizes(os.path.join(root, "data/reference/genome.chrom.sizes"))
    genes = generate_annotation(annotation_gtf)
    generate_refgene_bed(refgene_bed, genes)
    print(f"  Annotation contains {len(genes)} synthetic transcript models.")

    print("[3/6] Transcripts extraction ...")
    transcripts = extract_transcripts(genome_seqs, genes)

    print("[4/6] STAR Genome index ...")
    generate_star_index(os.path.join(root, "data/reference/star_index"), genome_fa, annotation_gtf)

    print(f"[5/6] Paired-end FASTQs ({READS_PER_SAMPLE} reads/sample) ...")
    ref_data = ReferenceData(
        genome_seqs=genome_seqs,
        genes=genes,
        transcripts=transcripts,
    )
    for sample in SAMPLES:
        generate_fastq_paired(
            os.path.join(root, f"data/fastq/{sample}_R1.fastq.gz"),
            os.path.join(root, f"data/fastq/{sample}_R2.fastq.gz"),
            ref_data,
        )
        print(f"  {sample} ✓")

    print("[6/6] Sample sheet ...")
    generate_samples_tsv(os.path.join(root, "data/samples.tsv"), root)

    print("\n" + "=" * 60)
    print("Test data generated successfully.")


if __name__ == "__main__":
    main()
