# Pipeline Execution Scripts

Bash wrappers that automate environment checking, configuration validation, and job orchestration.

---

## Execution Flow

```mermaid
graph TD
    A([User runs run_pipeline.sh]) --> B{Snakemake in PATH?}
    B -- No --> C[Activate Conda env from envs/main.yaml]
    B -- Yes --> D
    C --> D[Find config.yaml & Snakefile]
    
    D --> E((validate_config.py))
    E -- Error --> F[Print error & halt]
    E -- Success --> G[Launch Snakemake]
    
    G --> H{Profile passed?}
    H -- Yes --> I[Apply profile settings]
    H -- No --> J[Use CLI args only]
    
    I --> K[Pipeline running]
    J --> K
```

---

## Script Reference

| Script | Purpose | Usage |
|---|---|---|
| `run_pipeline.sh` | Main pipeline orchestrator. Runs pre-flight checks, schema validation, and configures concurrent workers. | `scripts/run_pipeline.sh [options] [-- <snakemake args>]` |
| `clean_result_files.sh` | Safely purges temporary run files (`results/`, `logs/`, `benchmarks/`) to prepare for a fresh start. | `scripts/clean_result_files.sh` |
| `directory_structure.sh` | Helper that verifies write permissions by constructing the outputs tree. | `scripts/directory_structure.sh` |

---

## `run_pipeline.sh` Configuration Options

| Flag | Meaning | Example |
|---|---|---|
| `-c, --cores N` | Allocates the maximum CPU cores to use | `-c 12` |
| `-f, --config PATH` | Custom YAML configuration file path | `-f configs/dev.yaml` |
| `-s, --snakefile PATH` | Custom entry-point Snakefile | `-s custom.smk` |
| `-l, --log PATH` | Redirects Snakemake execution logs | `-l run.log` |
| `-n, --dry-run` | Prints execution plan without running shell commands | `-n` |
| `--no-use-conda` | Disables automated Conda env deployment | `--no-use-conda` |
| `--keep-going` | Continues execution of independent jobs on failure | `--keep-going` |
| `--unlock` | Unlocks Snakemake directory locks | `--unlock` |
| `--` | Appends any raw Snakemake argument directly | `-- --profile profiles/local` |
