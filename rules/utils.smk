def is_single_end(sample):
    r2 = FASTQ_R2.get(sample)
    if not r2:
        return True
    if isinstance(r2, str) and r2.strip() == "":
        return True
    return False
