rule normalize_counts:
    input:
        counts=config['deseq2_prep']['input']['counts']

    output:
        tpm=config['normalize']['output']['tpm'],
        fpkm=config['normalize']['output']['fpkm']

    resources:
        mem_mb=2000,
        time="00:30:00"

    benchmark: "benchmarks/normalize/normalize.txt"
    log: "logs/normalize/normalize.log"
    conda: get_conda_env("envs/deseq2.yaml")
    container: "docker://quay.io/biocontainers/pandas:1.5.2"
    threads: 1

    message:
        "[NORMALIZE] Generating TPM and FPKM matrices from: {input.counts}"

    shell:
        """
        set -euo pipefail && \
        python3 rules/scripts/normalize.py \
        --counts {input.counts} \
        --tpm {output.tpm} \
        --fpkm {output.fpkm} \
        2> {log}
        """
