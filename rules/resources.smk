import os
from pathlib import Path

def get_input_size_mb(input_files):
    """Calculate the total size of input files in MB."""
    total_bytes = 0
    if not input_files:
        return 1.0
    
    # Handle single file, list, dict, or namedlist
    if isinstance(input_files, (str, Path)):
        files = [input_files]
    elif hasattr(input_files, "values"):
        files = list(input_files.values())
    else:
        files = list(input_files)

    for f in files:
        p = Path(str(f))
        if p.exists():
            total_bytes += p.stat().st_size
        else:
            # Fallback for dry runs or when files aren't built yet
            total_bytes += 100 * 1024 * 1024
            
    return max(1.0, total_bytes / (1024 * 1024))

def minutes_to_time_str(minutes):
    """Convert minutes to HH:MM:SS format."""
    minutes = max(1, int(minutes))
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}:00"

def allocate_memory(wildcards, input, attempt, **kwargs):
    """
    Predict memory based on input size (MB) and attempt number.
    Memory scales exponentially with attempt.
    """
    # Pull parameters from config or kwargs, with defaults
    base_mb = kwargs.get('base_mb', config.get('resources_dynamic', {}).get('memory', {}).get('base_mb', 2000))
    multiplier = kwargs.get('multiplier', config.get('resources_dynamic', {}).get('memory', {}).get('multiplier', 2.0))
    max_mb = kwargs.get('max_mb', config.get('resources_dynamic', {}).get('memory', {}).get('max_mb', 64000))
    
    size_mb = get_input_size_mb(input)
    scale = 2 ** (attempt - 1)
    mem = base_mb + (size_mb * multiplier) * scale
    return min(int(mem), max_mb)

def allocate_time(wildcards, input, attempt, **kwargs):
    """
    Predict time based on input size (MB) and attempt number.
    Time scales by 1.5x with attempt.
    """
    # Pull parameters from config or kwargs, with defaults
    base_minutes = kwargs.get('base_minutes', config.get('resources_dynamic', {}).get('time_alloc', {}).get('base_minutes', 30))
    multiplier = kwargs.get('multiplier', config.get('resources_dynamic', {}).get('time_alloc', {}).get('multiplier', 0.1))
    max_minutes = kwargs.get('max_minutes', config.get('resources_dynamic', {}).get('time_alloc', {}).get('max_minutes', 1440))
    
    size_mb = get_input_size_mb(input)
    scale = 1.5 ** (attempt - 1)
    minutes = base_minutes + (size_mb * multiplier) * scale
    minutes = min(int(minutes), max_minutes)
    return minutes_to_time_str(minutes)
