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
        overhang = config['star']['params']['sjdbOverhang'],
        reads = lambda w, input: f"{input.R1}" if is_single_end(w.sample) else f"{input.R1} {input.R2}"

    resources:
        mem_mb = lambda wildcards, input, attempt: allocate_memory(wildcards, input, attempt, base_mb=config['star']['resources']['mem_mb'], multiplier=3.0),
        time = lambda wildcards, input, attempt: allocate_time(wildcards, input, attempt)

    benchmark: "benchmarks/star/{sample}.txt"
    log: "logs/star/{sample}.log"
    conda: get_conda_env("envs/star.yaml", workflow)
    container: "docker://quay.io/biocontainers/star:2.7.11b--h5ca1c30_4"
    threads: config['star']['threads']

    message:
        "[STAR ALIGN] SAMPLE: {wildcards.sample} | INPUT: {input.R1} {input.R2} | OUTPUT: {output.bam}"

    shell:
        """
        set -euo pipefail && \
        STAR \
        --runThreadN {threads} \
        --genomeDir {params.index} \
        --readFilesIn {params.reads} \
        --readFilesCommand zcat \
        --sjdbOverhang {params.overhang} \
        --outSAMtype BAM Unsorted \
        --quantMode GeneCounts \
        --outFileNamePrefix {params.out_prefix} \
        2> {log}
        """
