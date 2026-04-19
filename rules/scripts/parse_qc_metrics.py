#!/usr/bin/env python3
"""Robustly parse and validate RNA-seq QC metrics from samtools stats."""

import sys
import argparse
from pathlib import Path

def parse_samtools_stats(stats_path):
    """Parses total reads, mapping rate, and duplicate count from samtools stats."""
    metrics = {
        "total_reads": None,
        "mapped_reads": None,
        "mapped_properly": None,
        "duplicates": None
    }
    try:
        with open(stats_path, 'r') as f:
            for line in f:
                if not line.startswith("SN\t"):
                    continue
                if "sequences:" in line:
                    metrics["total_reads"] = int(line.split('\t')[2])
                elif "reads mapped:" in line and "reads mapped and paired" not in line:
                    metrics["mapped_reads"] = int(line.split('\t')[2])
                elif "percentage of properly paired reads:" in line:
                    metrics["mapped_properly"] = float(line.split('\t')[2].replace('%', ''))
                elif "reads duplicated:" in line:
                    metrics["duplicates"] = int(line.split('\t')[2])
    except Exception as e:
        print(f"Error parsing samtools stats: {e}", file=sys.stderr)
    return metrics

def main():
    parser = argparse.ArgumentParser(description="Process RNA-seq QC metrics.")
    parser.add_argument("--sample", required=True)
    parser.add_argument("--stats-file", required=True)
    parser.add_argument("--min-total-reads", type=int, required=True)
    parser.add_argument("--min-mapping-rate", type=float, required=True)
    parser.add_argument("--max-duplicate-rate", type=float, required=True)
    parser.add_argument("--log", required=True)
    parser.add_argument("--output", required=True)
    
    args = parser.parse_args()
    
    errors = []
    log_content = [f"QC Report for {args.sample}", "-------------------------------"]
    
    stats = parse_samtools_stats(args.stats_file)
    
    if stats["total_reads"] is None: errors.append("Total Reads")
    if stats["mapped_reads"] is None: errors.append("Mapped Reads")
    if stats["duplicates"] is None: errors.append("Duplicates")
    
    if errors:
        Path(args.log).parent.mkdir(parents=True, exist_ok=True)
        with open(args.log, 'w') as f:
            f.write("\n".join(log_content) + "\n")
            f.write(f"[ERROR] Failed to parse metrics: {', '.join(errors)}\n")
        sys.exit(1)
        
    mapping_rate = (stats["mapped_reads"] * 100.0 / stats["total_reads"]) if stats["total_reads"] > 0 else 0.0
    dup_rate = (stats["duplicates"] * 100.0 / stats["total_reads"]) if stats["total_reads"] > 0 else 100.0
    
    log_content.append(f"Total Reads: {stats['total_reads']:,} (Target: >= {args.min_total_reads:,})")
    log_content.append(f"Mapping Rate (%): {mapping_rate:.2f} (Target: >= {args.min_mapping_rate})")
    log_content.append(f"Duplicate Rate (%): {dup_rate:.2f} (Target: <= {args.max_duplicate_rate})")
    
    failures = []
    if stats["total_reads"] < args.min_total_reads:
        failures.append(f"Total Reads {stats['total_reads']:,} < {args.min_total_reads:,}")
    if mapping_rate < args.min_mapping_rate:
        failures.append(f"Mapping Rate {mapping_rate:.2f}% < {args.min_mapping_rate}%")
    if dup_rate > args.max_duplicate_rate:
        failures.append(f"Duplicate Rate {dup_rate:.2f}% > {args.max_duplicate_rate}%")
    
    if failures:
        log_content.append("-------------------------------")
        log_content.append("RESULT: FAILED")
        for fail in failures:
            log_content.append(f"[QC FAILURE] {fail}")
        Path(args.log).parent.mkdir(parents=True, exist_ok=True)
        with open(args.log, 'w') as f:
            f.write("\n".join(log_content) + "\n")
        print("\n".join(log_content), file=sys.stderr)
        sys.exit(2)
        
    log_content.append("-------------------------------")
    log_content.append("RESULT: PASSED")
    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    with open(args.log, 'w') as f:
        f.write("\n".join(log_content) + "\n")
        
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w') as f:
        f.write(f"{args.sample}\tPASSED\n")

if __name__ == "__main__":
    main()
