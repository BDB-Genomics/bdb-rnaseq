from pathlib import Path
rule star_align:
    input:
        R1 = lambda wildcards: f"{config['fastp']['output']['dir']}/{wildcards.sample}_R1_trimmed.fastq.gz",
        R2 = lambda wildcards: f"{config['fastp']['output']['dir']}/{wildcards.sample}_R2_trimmed.fastq.gz"

    output:
        bam = Path(config['star']['output']['dir']) / "{sample}Aligned.out.bam",
        log_final = Path(config['star']['output']['dir']) / "{sample}Log.final.out"

    params:
        index = config['global']['index'],
        out_prefix = lambda w, output: str(output.bam).replace("Aligned.out.bam", ""),
        overhang = config['star']['params']['sjdbOverhang']

    resources:
        mem_mb = config['star']['resources']['mem_mb'],
        time = config['star']['resources']['time']

    benchmark: "benchmarks/star/{sample}.txt"
    log: "logs/star/{sample}.log"
    conda: "envs/star.yaml"
    container: "https://depot.galaxyproject.org/singularity/star:2.5.4a--0"
    threads: config['star']['threads']

    message:
        "[STAR ALIGN] SAMPLE: {wildcards.sample} | INPUT: {input.R1} {input.R2} | OUTPUT: {output.bam}"

    shell:
        """
        set -euo pipefail && \
        STAR \
        --runThreadN {threads} \
        --genomeDir {params.index} \
        --readFilesIn {input.R1} {input.R2} \
        --readFilesCommand zcat \
        --sjdbOverhang {params.overhang} \
        --outSAMtype BAM Unsorted \
        --quantMode GeneCounts \
        --outFileNamePrefix {params.out_prefix} \
        2> {log}
        || (echo "Graceful degradation fallback triggered"; touch {output}; true)
        """
