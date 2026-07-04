from pathlib import Path
rule deseq2_prep:
    input:
        counts=config['deseq2_prep']['input']['counts'],
        samples=config['deseq2_prep']['input']['samples']

    output:
        normalized_counts=Path(config['deseq2_prep']['output']['dir']) / "normalized_counts.txt",
        pca=Path(config['deseq2_prep']['output']['dir']) / "pca.txt",
        sample_correlation=Path(config['deseq2_prep']['output']['dir']) / "sample_correlation.txt",
        dispersions=Path(config['deseq2_prep']['output']['dir']) / "dispersions.txt",
        gene_filter=Path(config['deseq2_prep']['output']['dir']) / "genes_filtered.txt"

    params:
        min_mean_expr=config['deseq2_prep']['params']['min_mean_expr'],
        padj_threshold=config['deseq2_prep']['params']['padj_threshold'],
        output_dir=lambda w, output: os.path.dirname(output.normalized_counts)

    resources:
        mem_mb=config['deseq2_prep']['resources']['mem_mb'],
        time=config['deseq2_prep']['resources']['time']

    benchmark: "benchmarks/deseq2_prep/deseq2_prep.txt"
    log: "logs/deseq2_prep/deseq2_prep.log"
    conda: "rules/envs/deseq2.yaml"
    container: "docker://python:3.10"
    threads: config['deseq2_prep']['threads']

    message:
        "[DESEQ2_PREP] INPUT: {input.counts} | OUTPUT: {output.normalized_counts}"

    shell:
        """
        set -euo pipefail && \
        python3 rules/scripts/deseq2_prep.py \
        --counts {input.counts} \
        --samples {input.samples} \
        --output-dir {params.output_dir} \
        --min-mean-expr {params.min_mean_expr} \
        --padj-threshold {params.padj_threshold} \
        2> {log}
        """