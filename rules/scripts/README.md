# Pipeline Scripts

Python utilities for validation, QC gating, normalization, analytics, and CI/CD test data generation.

---

## How Scripts Fit into the Pipeline

```mermaid
graph TD
    Start((Pipeline Start)) --> V[validate_config.py]
    V -- Fail --> Halt1[Exit 1]
    V -- Pass --> DAG[Snakemake DAG]

    DAG --> QC[parse_qc_metrics.py]
    QC -- Fails --> Halt2[Flag FAILED]
    QC -- Passes --> FC[featureCounts]

    FC --> N[normalize.py]
    FC --> D[deseq2_prep.py]
    
    N --> End((Pipeline Finish))
    D --> End
    Halt2 --> End
    End --> A[aggregate_logs.py]
    A --> JSON((pipeline_execution_summary.json))

    classDef script fill:#cce5ff,stroke:#004085,color:#004085;
    classDef halt fill:#f8d7da,stroke:#dc3545,color:#721c24;
    classDef artifact fill:#fff3cd,stroke:#856404,color:#856404;

    class V,QC,N,D,A script;
    class Halt1,Halt2 halt;
    class JSON artifact;
```

---

## Script Reference

| Script | When it runs | What it does |
|---|---|---|
| `validate_config.py` | Before DAG | Checks all `config.yaml` keys, types, and file paths exist |
| `parse_qc_metrics.py` | After alignment | Reads total reads, mapping rate, duplicate rate. Flags samples as PASS or FAIL |
| `normalize.py` | After featureCounts | Computes FPKM and TPM from the raw count matrix |
| `deseq2_prep.py` | After featureCounts | VST-like normalization, PCA on top-500 variable genes, Pearson correlation matrix |
| `run_batched.py` | Manual use | Splits samples into batches for sequential Snakemake runs on low-memory machines |
| `aggregate_logs.py` | After completion | Collects benchmark and log data into a single JSON summary |
| `generate_test_data.py` | CI/CD only | Creates synthetic genome, STAR index, and paired-end FASTQs for automated testing |
| `test_validate_config.py` | CI/CD only | Unit tests for `validate_config.py` |

---

## Fail-Safe Behavior

| Script | Failure case | What happens |
|---|---|---|
| `validate_config.py` | Missing key or invalid path | Exits with code 1 before any job runs |
| `parse_qc_metrics.py` | Cannot parse a metric value | Defaults to `0.0` and flags the sample as `FAILED` |
| `deseq2_prep.py` | No sample names match between counts and sample sheet | Prints error to stderr, exits with code 1 |
| `deseq2_prep.py` | Division by zero in VST normalization | Stabilized with `+ 0.1` in the variance denominator |
| `deseq2_prep.py` | Log of zero in rlog | Stabilized with `+ alpha` before the `log2` transform |
| `normalize.py` | Zero-length gene or zero library size | Writes `0.0` instead of crashing |

---

## Script Flowcharts

### 1. `validate_config.py`
<details>
<summary>▶ Click to expand</summary>

```mermaid
graph TD
    A[config.yaml] --> B(Load & Parse YAML)
    B --> C{Valid syntax?}
    C -- No --> D[Exit 1]
    C -- Yes --> E(Scan .smk rules for config keys)
    E --> F{All keys present?}
    F -- No --> D
    F -- Yes --> G(Check types & file paths)
    G --> H{All valid?}
    H -- No --> D
    H -- Yes --> I[Exit 0 — Proceed]
```

</details>

### 2. `parse_qc_metrics.py`
<details>
<summary>▶ Click to expand</summary>

```mermaid
graph TD
    A[BAM Stats File] --> B(Load metrics)
    B --> C{Parseable?}
    C -- No --> D[Default to 0.0, flag FAILED]
    C -- Yes --> E(Check reads, mapping rate, dup rate)
    E --> F{Thresholds met?}
    F -- No --> G[Flag FAILED]
    F -- Yes --> H[Flag PASSED]
    D --> I(Write to log)
    G --> I
    H --> I
    I --> J{Any failures?}
    J -- Yes --> K[Exit 1]
    J -- No --> L[Exit 0]
```

</details>

### 3. `normalize.py`
<details>
<summary>▶ Click to expand</summary>

```mermaid
graph TD
    A[counts.txt + GTF] --> B(Parse count matrix)
    B --> C(Compute gene lengths from GTF)
    C --> D(Calculate FPKM per sample)
    D --> E(Calculate TPM per sample)
    E --> F(Write FPKM and TPM matrices)
    F --> G[Exit 0]
```

</details>

### 4. `deseq2_prep.py`
<details>
<summary>▶ Click to expand</summary>

```mermaid
graph TD
    A[counts.txt + samples.tsv] --> B(Parse counts & metadata)
    B --> C{Sample names match?}
    C -- No --> D[stderr error & Exit 1]
    C -- Yes --> E(Filter low-expressed genes)
    E --> F(Normalize via VST-like log2 transform)
    F --> G(PCA on top-500 variable genes)
    G --> H(Pearson sample correlation)
    H --> I(Write all outputs)
    I --> J[Exit 0]
```

</details>

### 5. `run_batched.py`
<details>
<summary>▶ Click to expand</summary>

```mermaid
graph TD
    A[samples.tsv] --> B(Validate sample name regex)
    B --> C{Invalid characters?}
    C -- Yes --> D[Exit 1]
    C -- No --> E(Split into batches)
    E --> F{Dry run?}
    F -- Yes --> G[Print batches & Exit 0]
    F -- No --> H(Run Snakemake per batch)
    H --> I[Run final MultiQC]
```

</details>

### 6. `aggregate_logs.py`
<details>
<summary>▶ Click to expand</summary>

```mermaid
graph TD
    A[benchmarks/ + logs/] --> B{Pipeline failed?}
    B -- Yes --> C(Scan logs for errors)
    C --> D(Filter false-positive warnings)
    D --> E(Collect real errors)
    B -- No --> F(Parse benchmark times & memory)
    F --> G(Build telemetry report)
    E --> G
    G --> H[pipeline_execution_summary.json]
```

</details>

### 7. `generate_test_data.py`
<details>
<summary>▶ Click to expand</summary>

```mermaid
graph TD
    A[Start] --> B(Build synthetic genome & GTF)
    B --> C(Generate FASTA & chrom.sizes)
    C --> D{STAR on PATH?}
    D -- No --> E[Raise FileNotFoundError]
    D -- Yes --> F(Build STAR index)
    F --> G(Simulate paired-end FASTQs)
```

</details>
