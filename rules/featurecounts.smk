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
        gtf=config['global']['gtf'],
        rseqc_reports=expand(
            f"{config['rseqc']['output']['dir']}/{{sample}}.infer_experiment.txt",
            sample=SAMPLES
        )

    output:
        counts=f"{config['featurecounts']['output']['dir']}/counts.txt",
        summary=f"{config['featurecounts']['output']['dir']}/counts.txt.summary"

    params:
        strand=lambda wildcards, input: get_consensus_strandedness(
            input.rseqc_reports,
            threshold=config['featurecounts']['params'].get('strandedness_threshold', 0.8),
            ci_mode=config.get('ci_mode', False),
            fallback=config['featurecounts']['params'].get('strandedness_fallback', 2)
        ),
        feature_type=config['featurecounts']['params']['feature_type'],
        attribute=config['featurecounts']['params']['attribute'],
        pe_flag=lambda w: "" if any(is_single_end(s) for s in SAMPLES) else "-p --countReadPairs"

    resources:
        mem_mb = lambda wildcards, input, attempt: allocate_memory(wildcards, input, attempt, base_mb=config['featurecounts']['resources']['mem_mb']),
        time = lambda wildcards, input, attempt: allocate_time(wildcards, input, attempt)

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
        {params.pe_flag} \
        --ignoreDup \
        -s {params.strand} \
        -t {params.feature_type} \
        -g {params.attribute} \
        -a {input.gtf} \
        -o {output.counts} \
        {input.bams} \
        2> {log}
        """
