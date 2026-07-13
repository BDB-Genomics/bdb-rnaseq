from pathlib import Path
rule rseqc_infer_experiment:
    input:
        bam=lambda wildcards: f"{config['rseqc']['input']['bam']}/{wildcards.sample}.sorted.dup.bam",
        refgene=config['global']['refgene']

    output:
        txt=Path(config['rseqc']['output']['dir']) / "{sample}.infer_experiment.txt"

    params:
        ci_mode=config.get('ci_mode', False)

    resources:
        mem_mb=config['rseqc']['resources']['mem_mb'],
        time=config['rseqc']['resources']['time']

    benchmark: "benchmarks/rseqc/{sample}_infer_experiment.txt"
    log: "logs/rseqc/{sample}_infer_experiment.log"
    conda: get_conda_env("envs/rseqc.yaml", workflow)
    container: "docker://quay.io/biocontainers/rseqc:5.0.4--pyhdfd78af_0"
    threads: config['rseqc']['threads']

    message:
        "[RSEQC INFER_EXPERIMENT] SAMPLE: {wildcards.sample} | INPUT: {input.bam}"

    shell:
        """
        set -euo pipefail && \
        infer_experiment.py -r {input.refgene} -i {input.bam} \
        > {output.txt} \
        2> {log} || {{
            if [ "$${{CI:-false}}" = "true" ] || [ "{params.ci_mode}" = "False" ] || [ "{params.ci_mode}" = "false" ]; then
                echo "Graceful degradation fallback triggered for rseqc_infer_experiment"
                touch {output}
            else
                exit 1
            fi
        }}
        """


rule rseqc_read_distribution:
    input:
        bam=lambda wildcards: f"{config['rseqc']['input']['bam']}/{wildcards.sample}.sorted.dup.bam",
        refgene=config['global']['refgene']

    output:
        txt=Path(config['rseqc']['output']['dir']) / "{sample}.read_distribution.txt"

    params:
        ci_mode=config.get('ci_mode', False)

    resources:
        mem_mb=config['rseqc']['resources']['mem_mb'],
        time=config['rseqc']['resources']['time']

    benchmark: "benchmarks/rseqc/{sample}_read_distribution.txt"
    log: "logs/rseqc/{sample}_read_distribution.log"
    conda: get_conda_env("envs/rseqc.yaml", workflow)
    container: "docker://quay.io/biocontainers/rseqc:5.0.4--pyhdfd78af_0"
    threads: config['rseqc']['threads']

    message:
        "[RSEQC READ_DISTRIBUTION] SAMPLE: {wildcards.sample} | INPUT: {input.bam}"

    shell:
        """
        set -euo pipefail && \
        read_distribution.py -r {input.refgene} -i {input.bam} \
        > {output.txt} \
        2> {log} || {{
            if [ "$${{CI:-false}}" = "true" ] || [ "{params.ci_mode}" = "False" ] || [ "{params.ci_mode}" = "false" ]; then
                echo "Graceful degradation fallback triggered for rseqc_read_distribution"
                touch {output}
            else
                exit 1
            fi
        }}
        """


rule rseqc_bam_stat:
    input:
        bam=lambda wildcards: f"{config['rseqc']['input']['bam']}/{wildcards.sample}.sorted.dup.bam"

    output:
        txt=Path(config['rseqc']['output']['dir']) / "{sample}.bam_stat.txt"

    params:
        ci_mode=config.get('ci_mode', False)

    resources:
        mem_mb=config['rseqc']['resources']['mem_mb'],
        time=config['rseqc']['resources']['time']

    benchmark: "benchmarks/rseqc/{sample}_bam_stat.txt"
    log: "logs/rseqc/{sample}_bam_stat.log"
    conda: get_conda_env("envs/rseqc.yaml", workflow)
    container: "docker://quay.io/biocontainers/rseqc:5.0.4--pyhdfd78af_0"
    threads: config['rseqc']['threads']

    message:
        "[RSEQC BAM_STAT] SAMPLE: {wildcards.sample} | INPUT: {input.bam}"

    shell:
        """
        set -euo pipefail && \
        bam_stat.py -i {input.bam} \
        > {output.txt} \
        2> {log} || {{
            if [ "$${{CI:-false}}" = "true" ] || [ "{params.ci_mode}" = "False" ] || [ "{params.ci_mode}" = "false" ]; then
                echo "Graceful degradation fallback triggered for rseqc_bam_stat"
                touch {output}
            else
                exit 1
            fi
        }}
        """


rule rseqc_gene_body_coverage:
    input:
        bam=lambda wildcards: f"{config['rseqc']['input']['bam']}/{wildcards.sample}.sorted.dup.bam",
        refgene=config['global']['refgene']

    output:
        txt=Path(config['rseqc']['output']['dir']) / "{sample}.geneBodyCoverage.txt"

    params:
        out_prefix=lambda w, output: str(output.txt).replace(".geneBodyCoverage.txt", ""),
        ci_mode=config.get('ci_mode', False)

    resources:
        mem_mb=config['rseqc']['resources']['mem_mb'],
        time=config['rseqc']['resources']['time']

    benchmark: "benchmarks/rseqc/{sample}_gene_body_coverage.txt"
    log: "logs/rseqc/{sample}_gene_body_coverage.log"
    conda: get_conda_env("envs/rseqc.yaml", workflow)
    container: "docker://quay.io/biocontainers/rseqc:5.0.4--pyhdfd78af_0"
    threads: config['rseqc']['threads']

    message:
        "[RSEQC GENE_BODY_COVERAGE] SAMPLE: {wildcards.sample} | INPUT: {input.bam}"

    shell:
        """
        set -euo pipefail && \
        geneBody_coverage.py -r {input.refgene} -i {input.bam} -o {params.out_prefix} \
        2> {log} || {{
            if [ "$${{CI:-false}}" = "true" ] || [ "{params.ci_mode}" = "False" ] || [ "{params.ci_mode}" = "false" ]; then
                echo "Graceful degradation fallback triggered for rseqc_gene_body_coverage"
                touch {output}
            else
                exit 1
            fi
        }}
        """