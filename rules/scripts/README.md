# Pipeline Scripts

Python utilities powering the RNA-seq pipeline's validation, QC, count matrix preparation, and telemetry.

---

## 🏗️ Integration Architecture

```mermaid
graph TD
    Start((Pipeline Start)) --> V[validate_config.py]
    V -- Fail --> Halt1[Exit 1]
    V -- Pass --> DAG[Snakemake DAG]

    DAG --> QC[parse_qc_metrics.py]
    QC -- Fails --> Halt2[Flag FAILED]
    QC -- Passes --> DESeq2[deseq2_prep.py]

    DESeq2 --> End((Pipeline Finish))
    Halt2 --> End
    End --> A[aggregate_logs.py]
    A --> JSON((pipeline_execution_summary.json))

    classDef script fill:#cce5ff,stroke:#004085,color:#004085;
    classDef halt fill:#f8d7da,stroke:#dc3545,color:#721c24;
    classDef artifact fill:#fff3cd,stroke:#856404,color:#856404;

    class V,QC,DESeq2,A script;
    class Halt1,Halt2 halt;
    class JSON artifact;
```

---

## 📁 Script Reference

| Script | When it Runs | Purpose |
|---|---|---|
| `validate_config.py` | Before DAG | Validates `config.yaml` keys, types, and physical paths before any job runs |
| `parse_qc_metrics.py` | After alignment | Checks total reads, mapping rate, and duplicate rate; flags samples that fail thresholds |
| `deseq2_prep.py` | After featureCounts | Normalizes counts (VST-like), computes PCA and sample correlation, writes dispersion estimates |
| `run_batched.py` | Manual invocation | Splits samples into batches for sequential Snakemake runs on memory-constrained machines |
| `aggregate_logs.py` | After completion | Collects benchmark and log data into a single JSON execution summary |
| `generate_test_data.py` | CI/CD only | Generates synthetic genomes, STAR indices, and paired-end FASTQs for automated testing |
| `test_validate_config.py` | CI/CD only | Unit tests for `validate_config.py` |

---

## 🔒 Fail-Safe Boundaries

| Script | Failure Scenario | Behavior |
|---|---|---|
| `parse_qc_metrics.py` | Metric parse failure | Defaults to `0.0`, flags sample as `FAILED` |
| `deseq2_prep.py` | Sample name mismatch between counts and sample sheet | Prints error to `stderr`, exits with code 1 |
| `deseq2_prep.py` | Division-by-zero in VST normalization | Stabilized with `+ 0.1` in variance denominator |
| `deseq2_prep.py` | Log-of-zero in rlog normalization | Stabilized with `+ alpha` before `log2` transform |

---

## 📊 Script Flowcharts

### 1. `validate_config.py` — Startup Validator
<details>
<summary>▶ Click to Expand</summary>

```mermaid
graph TD
    A[config.yaml] --> B(Load & Parse YAML)
    B --> C{Syntactically valid?}
    C -- No --> D[Exit 1]
    C -- Yes --> E(Scan .smk rules for config keys)
    E --> F{All keys present?}
    F -- No --> D
    F -- Yes --> G(Verify types & physical paths)
    G --> H{All valid?}
    H -- No --> D
    H -- Yes --> I[Exit 0 — Allow Execution]
```

</details>

### 2. `parse_qc_metrics.py` — QC Gate
<details>
<summary>▶ Click to Expand</summary>

```mermaid
graph TD
    A[BAM Stats File] --> B(Load sample metrics)
    B --> C{Values parseable?}
    C -- No --> D[Default to 0.0 & flag FAILED]
    C -- Yes --> E(Check reads, mapping rate, duplicate rate)
    E --> F{All thresholds met?}
    F -- No --> G[Flag FAILED]
    F -- Yes --> H[Flag PASSED]
    D --> I(Write to log)
    G --> I
    H --> I
    I --> J{Sample failed?}
    J -- Yes --> K[Exit 1]
    J -- No --> L[Exit 0]
```

</details>

### 3. `deseq2_prep.py` — Count Matrix Processor
<details>
<summary>▶ Click to Expand</summary>

```mermaid
graph TD
    A[counts.txt + samples.tsv] --> B(Parse counts & metadata)
    B --> C{Sample names overlap?}
    C -- No --> D[stderr error & Exit 1]
    C -- Yes --> E(Filter low-expressed genes)
    E --> F(Normalize via VST-like log2 transform)
    F --> G(PCA on top-500 variable genes)
    G --> H(Pearson sample correlation)
    H --> I(Write all outputs)
    I --> J[Exit 0]
```

</details>

### 4. `run_batched.py` — Batch Orchestrator
<details>
<summary>▶ Click to Expand</summary>

```mermaid
graph TD
    A[samples.tsv] --> B(Validate sample name regex)
    B --> C{Invalid characters?}
    C -- Yes --> D[Exit 1]
    C -- No --> E(Split into batches)
    E --> F{Dry run?}
    F -- Yes --> G[Print batches & Exit 0]
    F -- No --> H(Invoke Snakemake per batch sequentially)
    H --> I[Run final MultiQC]
```

</details>

### 5. `aggregate_logs.py` — Telemetry Aggregator
<details>
<summary>▶ Click to Expand</summary>

```mermaid
graph TD
    A[benchmarks/ + logs/] --> B{Pipeline failed?}
    B -- Yes --> C(Scan logs via rolling buffer)
    C --> D(Filter false-positive warnings)
    D --> E(Collect real errors)
    B -- No --> F(Parse benchmark times & memory)
    F --> G(Build telemetry report)
    E --> G
    G --> H[pipeline_execution_summary.json]
```

</details>

### 6. `generate_test_data.py` — CI/CD Synthetic Generator
<details>
<summary>▶ Click to Expand</summary>

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
