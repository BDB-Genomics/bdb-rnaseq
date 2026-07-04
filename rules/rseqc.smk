from pathlib import Path
rule rseqc_infer_experiment:
    input:
        bam=lambda wildcards: f"{config['rseqc']['input']['bam']}/{wildcards.sample}.sorted.dup.bam",
        refgene=config['global']['refgene']

    output:
        txt=Path(config['rseqc']['output']['dir']) / "{sample}.infer_experiment.txt"

    resources:
        mem_mb=config['rseqc']['resources']['mem_mb'],
        time=config['rseqc']['resources']['time']

    benchmark: "benchmarks/rseqc/{sample}_infer_experiment.txt"
    log: "logs/rseqc/{sample}_infer_experiment.log"
    conda: "envs/rseqc.yaml"
    container: "https://depot.galaxyproject.org/singularity/rseqc:5.0.3--py39h7a9f48d_1"
    threads: config['rseqc']['threads']

    message:
        "[RSEQC INFER_EXPERIMENT] SAMPLE: {wildcards.sample} | INPUT: {input.bam}"

    shell:
        """
        set -euo pipefail && \
        infer_experiment.py -r {input.refgene} -i {input.bam} \
        > {output.txt} \
        2> {log}
        """


rule rseqc_read_distribution:
    input:
        bam=lambda wildcards: f"{config['rseqc']['input']['bam']}/{wildcards.sample}.sorted.dup.bam",
        refgene=config['global']['refgene']

    output:
        txt=Path(config['rseqc']['output']['dir']) / "{sample}.read_distribution.txt"

    resources:
        mem_mb=config['rseqc']['resources']['mem_mb'],
        time=config['rseqc']['resources']['time']

    benchmark: "benchmarks/rseqc/{sample}_read_distribution.txt"
    log: "logs/rseqc/{sample}_read_distribution.log"
    conda: "envs/rseqc.yaml"
    container: "https://depot.galaxyproject.org/singularity/rseqc:5.0.3--py39h7a9f48d_1"
    threads: config['rseqc']['threads']

    message:
        "[RSEQC READ_DISTRIBUTION] SAMPLE: {wildcards.sample} | INPUT: {input.bam}"

    shell:
        """
        set -euo pipefail && \
        read_distribution.py -r {input.refgene} -i {input.bam} \
        > {output.txt} \
        2> {log}
        """


rule rseqc_bam_stat:
    input:
        bam=lambda wildcards: f"{config['rseqc']['input']['bam']}/{wildcards.sample}.sorted.dup.bam"

    output:
        txt=Path(config['rseqc']['output']['dir']) / "{sample}.bam_stat.txt"

    resources:
        mem_mb=config['rseqc']['resources']['mem_mb'],
        time=config['rseqc']['resources']['time']

    benchmark: "benchmarks/rseqc/{sample}_bam_stat.txt"
    log: "logs/rseqc/{sample}_bam_stat.log"
    conda: "envs/rseqc.yaml"
    container: "https://depot.galaxyproject.org/singularity/rseqc:5.0.3--py39h7a9f48d_1"
    threads: config['rseqc']['threads']

    message:
        "[RSEQC BAM_STAT] SAMPLE: {wildcards.sample} | INPUT: {input.bam}"

    shell:
        """
        set -euo pipefail && \
        bam_stat.py -i {input.bam} \
        > {output.txt} \
        2> {log}
        """


rule rseqc_gene_body_coverage:
    input:
        bam=lambda wildcards: f"{config['rseqc']['input']['bam']}/{wildcards.sample}.sorted.dup.bam",
        refgene=config['global']['refgene']

    output:
        txt=Path(config['rseqc']['output']['dir']) / "{sample}.geneBodyCoverage.txt"

    params:
        out_prefix=lambda w, output: str(output.txt).replace(".geneBodyCoverage.txt", "")

    resources:
        mem_mb=config['rseqc']['resources']['mem_mb'],
        time=config['rseqc']['resources']['time']

    benchmark: "benchmarks/rseqc/{sample}_gene_body_coverage.txt"
    log: "logs/rseqc/{sample}_gene_body_coverage.log"
    conda: "envs/rseqc.yaml"
    container: "https://depot.galaxyproject.org/singularity/rseqc:5.0.3--py39h7a9f48d_1"
    threads: config['rseqc']['threads']

    message:
        "[RSEQC GENE_BODY_COVERAGE] SAMPLE: {wildcards.sample} | INPUT: {input.bam}"

    shell:
        """
        set -euo pipefail && \
        geneBody_coverage.py -r {input.refgene} -i {input.bam} -o {params.out_prefix} \
        2> {log}
        """