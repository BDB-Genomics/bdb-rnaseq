from pathlib import Path


def is_single_end(sample):
    r2 = FASTQ_R2.get(sample)
    if not r2:
        return True
    if isinstance(r2, str) and r2.strip() == "":
        return True
    return False


def get_consensus_strandedness(report_paths, threshold=0.8, ci_mode=False, fallback=2):
    """
    Parses RSeQC infer_experiment output files and returns a single consensus
    strandedness flag (0 = unstranded, 1 = forward, 2 = reverse) for featureCounts.
    Raises ValueError if samples have conflicting strandedness.
    """
    if ci_mode:
        # In CI/test dry-run environments, return the fallback to prevent crashes
        return fallback

    results = []
    for path in report_paths:
        p = Path(path)
        if not p.exists() or p.stat().st_size == 0:
            # File is empty (could be touched in CI or dry-run)
            results.append(fallback)
            continue

        forward_frac = 0.0
        reverse_frac = 0.0
        with open(p, "r") as f:
            for line in f:
                if '"1++,1--"' in line or '"1++,2--"' in line:
                    parts = line.strip().split(":")
                    if len(parts) > 1:
                        forward_frac = float(parts[-1].strip())
                elif '"1+-,1-+"' in line or '"1+-,2-+"' in line:
                    parts = line.strip().split(":")
                    if len(parts) > 1:
                        reverse_frac = float(parts[-1].strip())

        if forward_frac >= threshold:
            results.append(1)
        elif reverse_frac >= threshold:
            results.append(2)
        else:
            results.append(0)

    if not results:
        return fallback

    # Check for consistency across all samples
    consensus = results[0]
    if any(r != consensus for r in results):
        # Format a helpful message for debugging
        sample_details = ", ".join(
            f"{Path(report_paths[i]).stem}: {results[i]}" for i in range(len(results))
        )
        raise ValueError(
            f"Mismatched strandedness detected across samples! Detailed layout: {sample_details}. "
            "Please ensure all samples in a single batch belong to the same sequencing library prep."
        )

    return consensus
