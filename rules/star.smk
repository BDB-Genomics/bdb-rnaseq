rule star_align:
    input:
        R1 = lambda wildcards: f"{config['fastp']['output']['dir']}/{wildcards.sample}_R1_trimmed.fastq.gz",
        R2 = lambda wildcards: f"{config['fastp']['output']['dir']}/{wildcards.sample}_R2_trimmed.fastq.gz"

    output:
        bam = f"{config['star']['output']['dir']}/{{sample}}Aligned.out.bam",
        log_final = f"{config['star']['output']['dir']}/{{sample}}Log.final.out"

    params:
        index = config['global']['index'],
        out_prefix = f"{config['star']['output']['dir']}/{{sample}}",
        overhang = config['star']['params']['sjdbOverhang']

    resources:  
        mem_mb = config['star']['resources']['mem_mb'],
        time = config['star']['resources']['time']

    benchmark: "benchmarks/star/{sample}.txt"
    log: "logs/star/{sample}.log"
    conda: "rules/envs/star.yaml"
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
        """
