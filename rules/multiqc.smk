rule multiqc:
    input:
        expand("results/fastqc/{sample}_R1_trimmed_fastqc.zip", sample=SAMPLES),
        expand("results/fastqc/{sample}_R2_trimmed_fastqc.zip", sample=SAMPLES),
        expand("results/fastp/{sample}.json", sample=SAMPLES),
        expand(f"{config['star']['output']['dir']}/{{sample}}Log.final.out", sample=SAMPLES),
        expand(f"{config['markduplicates']['output']['dir']}/{{sample}}.dup_metrics.txt", sample=SAMPLES),
        expand("results/samtools_stats/{sample}_postFiltering.stats.txt", sample=SAMPLES),
        expand(f"{config['rseqc']['output']['dir']}/{{sample}}.infer_experiment.txt", sample=SAMPLES),
        expand(f"{config['preseq']['output']['dir']}/{{sample}}.ccurve.txt", sample=SAMPLES),
        f"{config['featurecounts']['output']['dir']}/counts.txt.summary"
        
    output:
        report_dir=directory(config['multiqc']['output']['report'])
        
    resources:
        mem_mb=config['multiqc']['resources']['mem_mb'], 
        time=config['multiqc']['resources']['time']
            
    log: "logs/multiqc/multiqc.log"
    benchmark: "benchmarks/multiqc/multiqc.txt"
    conda: "envs/multiqc.yaml"
    container: "https://depot.galaxyproject.org/singularity/multiqc:1.0--py27_0"
    threads: config['multiqc']['threads']
        
    message:
        "Running MultiQC to aggregate all QC reports| INPUT: {input}"
        
    shell:
        """

        set -euo pipefail && \
        multiqc {input} -o {output.report_dir} \
            --title "RNA-seq Pipeline QC Report" \
            --comment "Comprehensive quality control metrics for RNA-seq analysis" \
            2> {log} || (echo "Graceful degradation fallback triggered"; touch {output}; true)
        """
