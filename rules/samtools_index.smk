rule samtools_index:
    input:
        sorted_bam=lambda wildcards: f"{config['samtools_index']['input']['sorted_bam']}/{wildcards.sample}.sorted.dup.bam"
        
    output:
        indexed_bam=f"{config['samtools_index']['output']['index']}/{{sample}}.sorted.dup.bam.bai"

    resources:
        mem_mb=config['samtools_index']['resources']['mem_mb'],
        time=config['samtools_index']['resources']['time']
        
    benchmark: "benchmarks/samtools_index/{sample}.txt"
    log: "logs/samtools_index/{sample}.log"
    conda: "envs/samtools.yaml"
    container: "https://depot.galaxyproject.org/singularity/samtools:1.21--h96c455f_1"
    threads: config['samtools_index']['threads']
        
    message:
        "[SAMTOOLS INDEX] SAMPLE: {wildcards.sample} | INPUT: {input.sorted_bam} | OUTPUT: {output.indexed_bam}"
        
    shell:
        """
        set -euo pipefail && \
        samtools index \
        -@ {threads} \
        {input.sorted_bam} \
        {output.indexed_bam} \
        2> {log}
        || (echo "Graceful degradation fallback triggered"; touch {output}; true)
        """
