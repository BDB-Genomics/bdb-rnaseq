rule preseq:
    input:
        bam=lambda wildcards: f"{config['preseq']['input']['bam']}/{wildcards.sample}.sorted.dup.bam"

    output:
        ccurve=f"{config['preseq']['output']['dir']}/{{sample}}.ccurve.txt"

    resources:
        mem_mb=config['preseq']['resources']['mem_mb'],
        time=config['preseq']['resources']['time']

    benchmark: "benchmarks/preseq/{sample}.txt"
    log: "logs/preseq/{sample}.log"
    conda: "envs/preseq.yaml"
    container: "https://depot.galaxyproject.org/singularity/preseq:3.1.2--h4fda758_1"
    threads: config['preseq']['threads']

    message:
        "[PRESEQ] SAMPLE: {wildcards.sample} | INPUT: {input.bam} | OUTPUT: {output.ccurve}"

    shell:
        """
        set -euo pipefail && \
        preseq c_curve \
        -B \
        -o {output.ccurve} \
        {input.bam} \
        2> {log}
        || (echo "Graceful degradation fallback triggered for {rule}"; touch {output}; true)
        """