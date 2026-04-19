rule markduplicates:
    input:
        bam=lambda wildcards: f"{config['markduplicates']['input']['dir']}/{wildcards.sample}.sorted.bam"

    output:
        bam=f"{config['markduplicates']['output']['dir']}/{{sample}}.sorted.dup.bam",
        metrics=f"{config['markduplicates']['output']['dir']}/{{sample}}.dup_metrics.txt"

    params:
        java_opts=config['markduplicates']['params']['java_opts'],
        duplicate_scoring_strategy=config['markduplicates']['params']['duplicate_scoring_strategy'],
        optical_duplicate_pixel_distance=config['markduplicates']['params']['optical_duplicate_pixel_distance']

    resources:
        mem_mb=config['markduplicates']['resources']['mem_mb'],
        time=config['markduplicates']['resources']['time']

    benchmark: "benchmarks/markduplicates/{sample}.txt"
    log: "logs/markduplicates/{sample}.log"
    conda: "rules/envs/picard.yaml"
    container: "https://depot.galaxyproject.org/singularity/picard:3.0.0--hdfd78af_0"
    threads: config['markduplicates']['threads']

    message:
        "[MARKDUPLICATES] SAMPLE: {wildcards.sample} | INPUT: {input.bam} | OUTPUT: {output.bam} | METRICS: {output.metrics}"

    shell:
        """
        set -euo pipefail && \
        picard MarkDuplicates \
        -I {input.bam} \
        -O {output.bam} \
        -M {output.metrics} \
        --DUPLICATE_SCORING_STRATEGY {params.duplicate_scoring_strategy} \
        --OPTICAL_DUPLICATE_PIXEL_DISTANCE {params.optical_duplicate_pixel_distance} \
        --java-options {params.java_opts} \
        2> {log}
        """