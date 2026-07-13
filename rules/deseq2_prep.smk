import os

rule deseq2_prep:
    input:
        counts=config['deseq2_prep']['input']['counts'],
        samples=config['deseq2_prep']['input']['samples']

    output:
        normalized_counts=os.path.join(config['deseq2_prep']['output']['dir'], "normalized_counts.txt"),
        pca=os.path.join(config['deseq2_prep']['output']['dir'], "pca.txt"),
        sample_correlation=os.path.join(config['deseq2_prep']['output']['dir'], "sample_correlation.txt"),
        dispersions=os.path.join(config['deseq2_prep']['output']['dir'], "dispersions.txt"),
        gene_filter=os.path.join(config['deseq2_prep']['output']['dir'], "genes_filtered.txt")

    params:
        min_mean_expr=config['deseq2_prep']['params']['min_mean_expr'],
        padj_threshold=config['deseq2_prep']['params']['padj_threshold'],
        output_dir=config['deseq2_prep']['output']['dir']

    resources:
        mem_mb=config['deseq2_prep']['resources']['mem_mb'],
        time=config['deseq2_prep']['resources']['time']

    benchmark: "benchmarks/deseq2_prep/deseq2_prep.txt"
    log: "logs/deseq2_prep/deseq2_prep.log"
    conda: get_conda_env("envs/deseq2.yaml", workflow)
    container: "docker://quay.io/biocontainers/bioconductor-deseq2:1.40.2--r43hf17093f_0"
    threads: config['deseq2_prep']['threads']

    message:
        "[DESEQ2_PREP] INPUT: {input.counts} | OUTPUT: {output.normalized_counts}"

    shell:
        """
        set -euo pipefail && \
        Rscript rules/scripts/deseq2_prep.R \
        {input.counts} \
        {input.samples} \
        {params.output_dir} \
        {params.min_mean_expr} \
        {params.padj_threshold} \
        2> {log}
        """