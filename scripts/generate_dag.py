import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

fig, ax = plt.subplots(1, 1, figsize=(18, 26))
ax.set_xlim(0, 18)
ax.set_ylim(0, 26)
ax.axis("off")
ax.set_title(
    "RNA-seq Pipeline DAG\n(Current vs Missing Rules)",
    fontsize=14,
    fontweight="bold",
    pad=15,
)


def draw_box(
    ax,
    x,
    y,
    w,
    h,
    label,
    sublabel="",
    color="#4472C4",
    text_color="white",
    missing=False,
):
    if missing:
        style = "dashed"
        edgecolor = "#C00000"
    else:
        style = "round,pad=0.05"
        edgecolor = "black"
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=style,
        facecolor=color,
        edgecolor=edgecolor,
        linewidth=2 if missing else 1.5,
    )
    ax.add_patch(box)
    if sublabel:
        ax.text(
            x + w / 2,
            y + h / 2 + 0.15,
            label,
            ha="center",
            va="center",
            fontsize=8,
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
            fontsize=8,
            fontweight="bold",
            color=text_color,
        )


def draw_arrow(ax, x1, y1, x2, y2, bidirectional=False):
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(arrowstyle="->", color="#555555", lw=1.5),
    )
    if bidirectional:
        ax.annotate(
            "",
            xy=(x1, y1 - 0.1),
            xytext=(x2, y2 - 0.1),
            arrowprops=dict(arrowstyle="->", color="#555555", lw=1.5),
        )


# Colors
EXISTING = "#4472C4"  # Blue - exists
MISSING = "#C00000"  # Red - needs to be added
CURRENT_OUTPUT = "#70AD47"  # Green - current outputs

# =============================================
# CURRENT RULES (Existing)
# =============================================

# INPUT
draw_box(ax, 7, 25, 4, 0.8, "INPUT", "FASTQ + Config + Samples", EXISTING)

# PREPROCESSING
draw_box(ax, 1, 23, 4, 0.7, "fastp", "Trim adapters", EXISTING)
draw_box(ax, 1, 22, 4, 0.7, "fastqc", "Quality check", EXISTING)

# ALIGNMENT
draw_box(ax, 7, 23, 4, 0.7, "star_align", "Splice-aware alignment", EXISTING)

# POST-ALIGNMENT (existing)
draw_box(ax, 7, 21.5, 4, 0.7, "samtools_sort", "Sort BAM", EXISTING)
draw_box(ax, 7, 20.5, 4, 0.7, "samtools_index", "Index BAM", EXISTING)
draw_box(ax, 7, 19.5, 4, 0.7, "samtools_stats", "Alignment stats", EXISTING)

# QUANTIFICATION
draw_box(ax, 1, 19.5, 4, 0.7, "featurecounts", "Gene quantification", EXISTING)

# QC GATE
draw_box(ax, 1, 17.5, 4, 0.7, "qc_gate", "QC threshold", EXISTING)

# REPORTING
draw_box(ax, 1, 15.5, 4, 0.7, "multiqc", "Aggregate QC", EXISTING)

# =============================================
# MISSING RULES (Need to be added)
# =============================================

# MISSING - duplicate_marking
draw_box(
    ax,
    13,
    21.5,
    4,
    0.7,
    "duplicate_marking",
    "PCR duplicate marking",
    MISSING,
    missing=True,
)

# MISSING - rnaseq_metrics
draw_box(
    ax,
    13,
    19.5,
    4,
    0.7,
    "rnaseq_metrics",
    "picard RNA-seq metrics",
    MISSING,
    missing=True,
)

# MISSING - bam_coverage
draw_box(
    ax, 13, 17.5, 4, 0.7, "bam_coverage", "BigWig generation", MISSING, missing=True
)

# MISSING - qualimap
draw_box(ax, 13, 15.5, 4, 0.7, "qualimap", "RNA-seq QC", MISSING, missing=True)

# MISSING - preseq
draw_box(ax, 13, 13.5, 4, 0.7, "preseq", "Library complexity", MISSING, missing=True)

# =============================================
# ARROWS - Current Flow
# =============================================

# INPUT -> fastp, fastqc
draw_arrow(ax, 9, 25, 5, 23.7)
draw_arrow(ax, 9, 25, 9, 23.7)

# fastp -> fastqc
draw_arrow(ax, 3, 23, 3, 22.7)

# fastp, fastqc -> star_align
draw_arrow(ax, 3, 22, 8.5, 23.3)
draw_arrow(ax, 5, 22, 8.5, 23.3)

# star_align -> samtools_sort
draw_arrow(ax, 9, 23, 9, 22.2)

# samtools_sort -> samtools_index
draw_arrow(ax, 9, 21.5, 9, 20.5)

# samtools_index -> samtools_stats
draw_arrow(ax, 9, 20.5, 9, 19.5)

# samtools_stats -> featurecounts
draw_arrow(ax, 9, 19.5, 5, 19.5)

# samtools_sort -> duplicate_marking (missing)
draw_arrow(ax, 11, 21.5, 13, 21.5)

# duplicate_marking -> rnaseq_metrics (missing)
draw_arrow(ax, 13, 21.5, 13, 19.5)

# rnaseq_metrics -> bam_coverage (missing)
draw_arrow(ax, 13, 19.5, 13, 17.5)

# samtools_stats -> qc_gate
draw_arrow(ax, 9, 19.5, 5, 18.2)

# qc_gate -> multiqc
draw_arrow(ax, 3, 17.5, 3, 16.2)

# featurecounts -> multiqc
draw_arrow(ax, 3, 18.8, 1.5, 15.5)

# =============================================
# LEGEND
# =============================================
legend_y = 12
ax.text(1, legend_y, "LEGEND:", fontsize=10, fontweight="bold")
ax.add_patch(
    FancyBboxPatch((1, legend_y - 0.7), 0.5, 0.4, facecolor=EXISTING, edgecolor="black")
)
ax.text(1.7, legend_y - 0.55, "Existing Rule", fontsize=8)
ax.add_patch(
    FancyBboxPatch(
        (4, legend_y - 0.7),
        0.5,
        0.4,
        facecolor=MISSING,
        edgecolor="#C00000",
        linestyle="--",
        linewidth=2,
    )
)
ax.text(4.7, legend_y - 0.55, "Missing Rule (needs to be added)", fontsize=8)

# =============================================
# MISSING RULES LIST
# =============================================
ax.text(13, 12.5, "MISSING RULES:", fontsize=10, fontweight="bold", color="#C00000")
missing_rules = [
    "duplicate_marking - picard MarkDuplicates",
    "rnaseq_metrics - picard CollectRnaSeqMetrics",
    "bam_coverage - deepTools bamCoverage",
    "qualimap - bamqc",
    "preseq - c_curve",
]
for i, rule in enumerate(missing_rules):
    ax.text(13, 12 - i * 0.6, f"• {rule}", fontsize=8, color="#666666")

# =============================================
# CURRENT OUTPUTS per rule
# =============================================
ax.text(1, 11, "CURRENT OUTPUTS:", fontsize=10, fontweight="bold", color="#70AD47")
outputs = [
    "fastp: _trimmed.fastq.gz, .json, .html",
    "fastqc: _fastqc.html, .zip",
    "star: Aligned.out.bam, Log.final.out",
    "samtools_sort: .sorted.bam",
    "samtools_index: .sorted.bam.bai",
    "samtools_stats: _postFiltering.stats.txt",
    "featurecounts: counts.txt, counts.txt.summary",
    "qc_gate: _qc_pass.txt / _qc_fail.txt",
    "multiqc: multiqc_report.html",
]
for i, out in enumerate(outputs):
    ax.text(1, 10.5 - i * 0.5, f"• {out}", fontsize=7, color="#666666")

plt.tight_layout()
plt.savefig(
    "/home/himanshu/RNA-seq/pipeline_dag.png",
    dpi=150,
    bbox_inches="tight",
    facecolor="white",
)
print("Saved: /home/himanshu/RNA-seq/pipeline_dag.png")
