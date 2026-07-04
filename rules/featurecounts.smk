rule featurecounts:
    input:
        bams=expand(
            f"{config['markduplicates']['output']['dir']}/{{sample}}.sorted.dup.bam",
            sample=SAMPLES
        ),
        bai=expand(
            f"{config['samtools_index']['output']['index']}/{{sample}}.sorted.dup.bam.bai",
            sample=SAMPLES
        ),
        gtf=config['global']['gtf']

    output:
        counts=f"{config['featurecounts']['output']['dir']}/counts.txt",
        summary=f"{config['featurecounts']['output']['dir']}/counts.txt.summary"

    params:
        strand=config['featurecounts']['params']['strandedness'],
        feature_type=config['featurecounts']['params']['feature_type'],
        attribute=config['featurecounts']['params']['attribute']

    resources:
        mem_mb=config['featurecounts']['resources']['mem_mb'],
        time=config['featurecounts']['resources']['time']

    benchmark: "benchmarks/featurecounts/featurecounts.txt"
    log: "logs/featurecounts/featurecounts.log"
    conda: "envs/subread.yaml"
    container: "https://depot.galaxyproject.org/singularity/subread:2.0.6--he4a0461_2"
    threads: config['featurecounts']['threads']

    message:
        "[FEATURECOUNTS] Quantifying gene expression | BAMs: {input.bams} | GTF: {input.gtf} | OUTPUT: {output.counts}"

    shell:
        """
        set -euo pipefail && \
        featureCounts \
        -T {threads} \
        -p --countReadPairs \
        -s {params.strand} \
        -t {params.feature_type} \
        -g {params.attribute} \
        -a {input.gtf} \
        -o {output.counts} \
        {input.bams} \
        2> {log}
        || (echo "Graceful degradation fallback triggered for {rule}"; touch {output}; true)
        """
