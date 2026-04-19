import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

fig, ax = plt.subplots(1, 1, figsize=(20, 28))
ax.set_xlim(0, 20)
ax.set_ylim(0, 28)
ax.axis("off")
ax.set_title(
    "RNA-seq Pipeline Flow Chart\nI/O Consistency & Data Dependencies",
    fontsize=16,
    fontweight="bold",
    pad=20,
)


def draw_box(ax, x, y, w, h, label, sublabel="", color="#4472C4", text_color="white"):
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.05",
        facecolor=color,
        edgecolor="black",
        linewidth=1.5,
    )
    ax.add_patch(box)
    if sublabel:
        ax.text(
            x + w / 2,
            y + h / 2 + 0.15,
            label,
            ha="center",
            va="center",
            fontsize=9,
            fontweight="bold",
            color=text_color,
        )
        ax.text(
            x + w / 2,
            y + h / 2 - 0.2,
            sublabel,
            ha="center",
            va="center",
            fontsize=7,
            color=text_color,
        )
    else:
        ax.text(
            x + w / 2,
            y + h / 2,
            label,
            ha="center",
            va="center",
            fontsize=9,
            fontweight="bold",
            color=text_color,
        )


def draw_arrow(ax, x1, y1, x2, y2, label=""):
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(arrowstyle="->", color="#555555", lw=1.5),
    )
    if label:
        ax.text(
            (x1 + x2) / 2,
            (y1 + y2) / 2 + 0.15,
            label,
            ha="center",
            va="bottom",
            fontsize=7,
            color="#666666",
        )


# Colors
INPUT_COLOR = "#70AD47"
PREPROC_COLOR = "#4472C4"
ALIGN_COLOR = "#ED7D31"
POST_COLOR = "#7030A0"
QUANT_COLOR = "#C00000"
QC_COLOR = "#FFC000"
REPORT_COLOR = "#00B0F0"

# INPUT SECTION
draw_box(ax, 7, 26.5, 6, 1, "INPUTS", "FASTQ, Config, Samples", INPUT_COLOR)
draw_box(ax, 6, 25.2, 3.5, 0.9, "checksums", "Verify integrity", "#5B9A5B")
draw_box(ax, 10.5, 25.2, 3.5, 0.9, "validate_config", "Check YAML", "#5B9A5B")
draw_box(ax, 8.25, 25.2, 1.5, 0.9, "samples.tsv", "Sample sheet", "#888888")

draw_arrow(ax, 10, 26.5, 8.25, 26.1)
draw_arrow(ax, 10, 26.5, 12.75, 26.1)
draw_arrow(ax, 8.25, 25.2, 8.25, 24.5)

# PREPROCESSING
draw_box(ax, 7, 23.2, 6, 1.2, "PREPROCESSING", "fastp + fastqc", PREPROC_COLOR)
draw_box(ax, 6.25, 21.5, 3, 0.9, "fastp", "Trim adapters\nR1+R2", PREPROC_COLOR)
draw_box(ax, 10.75, 21.5, 3, 0.9, "fastqc", "Quality control\nHTML/ZIP", PREPROC_COLOR)

draw_arrow(ax, 10, 23.2, 7.75, 22.4)
draw_arrow(ax, 10, 23.2, 12.25, 22.4)
draw_arrow(ax, 8.25, 24.5, 8.25, 24.4)

# Outputs of fastp
draw_box(ax, 5.5, 20.2, 4.5, 0.7, "_R1_trimmed.fastq.gz", "", "#9DC3E6")
draw_box(ax, 5.5, 19.3, 4.5, 0.7, "_R2_trimmed.fastq.gz", "", "#9DC3E6")
draw_box(ax, 10.25, 20.2, 4, 0.7, "_fastp.html", "", "#9DC3E6")
draw_box(ax, 10.25, 19.3, 4, 0.7, "_fastp.json", "", "#9DC3E6")

draw_arrow(ax, 6.25, 21.5, 7.75, 20.9)
draw_arrow(ax, 6.25, 21.5, 7.75, 20.9)
draw_arrow(ax, 11.75, 21.5, 12.25, 20.9)
draw_arrow(ax, 11.75, 21.5, 12.25, 20.9)

# fastqc outputs
draw_box(ax, 10.5, 18.2, 3.5, 0.7, "_fastqc.html/zip", "", "#9DC3E6")

# ALIGNMENT
draw_box(ax, 7, 16.8, 6, 1.2, "ALIGNMENT", "STAR (splice-aware)", ALIGN_COLOR)
draw_box(
    ax,
    7,
    14.8,
    6,
    1.8,
    "star_align",
    "input: trimmed R1+R2\nindex: STAR genome\noutput: Aligned.out.bam\nLog.final.out\nReadsPerGene.tab",
    ALIGN_COLOR,
)

draw_arrow(ax, 8.25, 19.3, 8.25, 18.5)
draw_arrow(ax, 10, 18.2, 10, 17.1)

# POST-ALIGNMENT
draw_box(ax, 7, 13.3, 6, 1.2, "POST-ALIGNMENT", "Sort, Index, Metrics", POST_COLOR)

# samtools_sort
draw_box(ax, 1, 11.3, 4, 0.9, "samtools_sort", "Sort BAM", POST_COLOR)
draw_box(ax, 1, 10.1, 4, 0.9, "samtools_index", "Index .bai", POST_COLOR)
draw_box(ax, 1, 8.9, 4, 0.9, "samtools_stats", "Stats txt", POST_COLOR)

# duplicate_marking
draw_box(
    ax, 7.5, 11.3, 4, 0.9, "duplicate_marking", "picard MarkDuplicates", POST_COLOR
)
draw_box(ax, 7.5, 10.1, 4, 0.9, "rnaseq_metrics", "picard RnaSeqMetrics", POST_COLOR)
draw_box(ax, 7.5, 8.9, 4, 0.9, "bam_coverage", "deepTools bamCoverage", POST_COLOR)

# bam_coverage output
draw_box(ax, 7.5, 7.7, 4, 0.9, ".bw BigWig", "Normalized for IGV", "#7030A0")

draw_arrow(ax, 10, 13.3, 9.5, 12.2)
draw_arrow(ax, 5, 14.8, 3, 12.2)
draw_arrow(ax, 3, 11.3, 3, 10.1)
draw_arrow(ax, 3, 10.1, 3, 9.8)
draw_arrow(ax, 9.5, 11.3, 9.5, 10.1)
draw_arrow(ax, 9.5, 10.1, 9.5, 9.8)
draw_arrow(ax, 9.5, 8.9, 9.5, 8.6)

# QUANTIFICATION
draw_box(ax, 7, 6.3, 6, 1.2, "QUANTIFICATION", "featurecounts", QUANT_COLOR)
draw_box(
    ax,
    6,
    4.6,
    8,
    1.4,
    "featurecounts",
    "input: indexed BAMs + GTF\noutput: counts.txt + summary",
    QUANT_COLOR,
)

draw_arrow(ax, 5, 8.9, 5, 7.5)
draw_arrow(ax, 10, 7.7, 10, 5.9)

# QC GATE
draw_box(ax, 7, 3.1, 6, 1.2, "QC GATE", "Threshold-based filtering", QC_COLOR)
draw_box(
    ax,
    5.5,
    1.5,
    9,
    1.3,
    "qc_gate",
    "checks: total reads, mapping rate,\nduplicate rate → pass.txt / fail.txt",
    QC_COLOR,
)

draw_arrow(ax, 10, 4.6, 10, 4.3)
draw_arrow(ax, 8, 3.1, 10, 2.8)

# REPORTING
draw_box(ax, 7, 0.3, 6, 1, "REPORTING", "multiqc aggregation", REPORT_COLOR)
draw_box(
    ax,
    5,
    -1.2,
    10,
    1.2,
    "multiqc",
    "Aggregates all QC reports\n→ multiqc_report.html",
    REPORT_COLOR,
)

draw_arrow(ax, 10, 1.5, 10, 1.3)
draw_arrow(ax, 8, 0.3, 10, -0.2)

# Legend
legend_y = 27.5
ax.text(1, legend_y, "LEGEND:", fontsize=10, fontweight="bold")
ax.add_patch(
    FancyBboxPatch(
        (1, legend_y - 0.6), 0.5, 0.35, facecolor=INPUT_COLOR, edgecolor="black"
    )
)
ax.text(1.7, legend_y - 0.45, "Input/Data", fontsize=8)
ax.add_patch(
    FancyBboxPatch(
        (4, legend_y - 0.6), 0.5, 0.35, facecolor=PREPROC_COLOR, edgecolor="black"
    )
)
ax.text(4.7, legend_y - 0.45, "Preprocessing", fontsize=8)
ax.add_patch(
    FancyBboxPatch(
        (7, legend_y - 0.6), 0.5, 0.35, facecolor=ALIGN_COLOR, edgecolor="black"
    )
)
ax.text(7.7, legend_y - 0.45, "Alignment", fontsize=8)
ax.add_patch(
    FancyBboxPatch(
        (10, legend_y - 0.6), 0.5, 0.35, facecolor=POST_COLOR, edgecolor="black"
    )
)
ax.text(10.7, legend_y - 0.45, "Post-Alignment", fontsize=8)
ax.add_patch(
    FancyBboxPatch(
        (1, legend_y - 1.1), 0.5, 0.35, facecolor=QUANT_COLOR, edgecolor="black"
    )
)
ax.text(1.7, legend_y - 0.95, "Quantification", fontsize=8)
ax.add_patch(
    FancyBboxPatch(
        (4, legend_y - 1.1), 0.5, 0.35, facecolor=QC_COLOR, edgecolor="black"
    )
)
ax.text(4.7, legend_y - 0.95, "QC Gate", fontsize=8)
ax.add_patch(
    FancyBboxPatch(
        (7, legend_y - 1.1), 0.5, 0.35, facecolor=REPORT_COLOR, edgecolor="black"
    )
)
ax.text(7.7, legend_y - 0.95, "Reporting", fontsize=8)
ax.add_patch(
    FancyBboxPatch(
        (10, legend_y - 1.1), 0.5, 0.35, facecolor="#9DC3E6", edgecolor="black"
    )
)
ax.text(10.7, legend_y - 0.95, "Intermediate Output", fontsize=8)

plt.tight_layout()
plt.savefig(
    "/home/himanshu/RNA-seq/pipeline_flowchart.png",
    dpi=150,
    bbox_inches="tight",
    facecolor="white",
)
print("Saved: /home/himanshu/RNA-seq/pipeline_flowchart.png")
