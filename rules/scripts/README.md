# Pipeline Scripts

Core Python utilities that power the RNA-seq pipeline's validation, quality control, count matrix preparation, and telemetry.

---

## 🏗️ Integration Architecture

```mermaid
graph TD
    Start((Pipeline Start)) --> V[validate_config.py]
    V -- Fail --> Halt1[Exit 1]
    V -- Pass --> DAG[Snakemake DAG]

    DAG --> QC[parse_qc_metrics.py]
    QC -- Sample Fails --> Halt2[Flag FAILED]
    QC -- Sample Passes --> Continue[Continue]

    DAG --> DESeq2[deseq2_prep.py]

    Continue --> End((Pipeline Finish))
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

### Python Scripts

| Script | When it Runs | Purpose |
|---|---|---|
| `validate_config.py` | Before DAG | Scans `.smk` files for config references, verifies keys exist, checks scalar types, confirms physical files |
| `parse_qc_metrics.py` | After alignment | Evaluates total read count, mapping rate, and duplicate rate against thresholds; flags failures |
| `deseq2_prep.py` | After featureCounts | Normalizes count matrix (VST-like), computes PCA and sample correlation, writes dispersion estimates |
| `run_batched.py` | Manual invocation | Batches samples for sequential Snakemake execution on low-memory machines |
| `aggregate_logs.py` | After completion | Streams `benchmarks/` and `logs/` into a single JSON summary; filters false-positive errors |
| `generate_test_data.py` | CI/CD only | Builds synthetic reference genomes, STAR indices, GTF annotations, and paired-end FASTQs for automated testing |
| `test_validate_config.py` | CI/CD only | Unit tests for `validate_config.py` |

---

## 🔒 Fail-Safe Boundaries

Every analytic script implements defensive error handling to prevent a single bad sample from crashing a multi-day cohort run:

| Script | Failure Scenario | Behavior |
|---|---|---|
| `parse_qc_metrics.py` | Parse failure | Defaults metrics to `0.0`, flags sample as `FAILED` |
| `deseq2_prep.py` | No sample name overlap between counts and sample sheet | Writes error message to `stderr`, exits with code 1 |
| `deseq2_prep.py` | Division-by-zero in VST normalization | Stabilized with `+ 0.1` offset in variance denominator |
| `deseq2_prep.py` | Log-of-zero in rlog normalization | Stabilized with `+ alpha` offset before `log2` transform |

---

## 📊 Script Flowcharts

### 1. `validate_config.py` (Startup Validator)
<details>
<summary>▶ Click to Expand Flowchart</summary>

```mermaid
graph TD
    A[config.yaml] --> B(Load & Parse YAML)
    B --> C{Syntactically Valid?}
    C -- No --> D[Exit 1]
    C -- Yes --> E(Scan .smk rules for config keys)
    E --> F{All keys present?}
    F -- No --> D
    F -- Yes --> G(Verify type bounds & physical path existence)
    G --> H{All valid?}
    H -- No --> D
    H -- Yes --> I[Exit 0 / Allow Execution]
```

</details>

### 2. `parse_qc_metrics.py` (QC Gate)
<details>
<summary>▶ Click to Expand Flowchart</summary>

```mermaid
graph TD
    A[BAM Stats File] --> B(Load metrics for sample)
    B --> C{Values present?}
    C -- No --> D[Set defaults to 0.0 & flag FAILED]
    C -- Yes --> E(Check total reads, mapping rate, duplicate rate against thresholds)
    E --> F{All thresholds met?}
    F -- No --> G[Flag sample FAILED]
    F -- Yes --> H[Flag sample PASSED]
    D --> I(Write metrics to log)
    G --> I
    H --> I
    I --> J{Did sample FAIL?}
    J -- Yes --> K[Exit 1 to halt downstream]
    J -- No --> L[Exit 0]
```

</details>

### 3. `deseq2_prep.py` (Count Matrix Processor)
<details>
<summary>▶ Click to Expand Flowchart</summary>

```mermaid
graph TD
    A[counts.txt + samples.tsv] --> B(Parse counts & sample metadata)
    B --> C{Sample names overlap?}
    C -- No --> D[Write error to stderr & Exit 1]
    C -- Yes --> E(Filter low-expressed genes by min mean threshold)
    E --> F(Normalize counts via VST-like log2 transform)
    F --> G(Compute PCA on top-500 variable genes)
    G --> H(Compute sample-to-sample Pearson correlation)
    H --> I(Write dispersions, filtered gene list, and all outputs)
    I --> J[Exit 0]
```

</details>

### 4. `run_batched.py` (Low-Resource Batch Orchestrator)
<details>
<summary>▶ Click to Expand Flowchart</summary>

```mermaid
graph TD
    A[samples.tsv] --> B(Validate sample names regex)
    B --> C{Contains traversal/invalid chars?}
    C -- Yes --> D[Exit 1]
    C -- No --> E(Chunk samples into batches)
    E --> F{Dry Run?}
    F -- Yes --> G[Print batches & Exit 0]
    F -- No --> H(Sequentially invoke Snakemake per batch)
    H --> I[Run final MultiQC on complete cohort]
```

</details>

### 5. `aggregate_logs.py` (Telemetry Aggregator)
<details>
<summary>▶ Click to Expand Flowchart</summary>

```mermaid
graph TD
    A[benchmarks/ + logs/] --> B{Pipeline failed?}
    B -- Yes --> C(Scan logs line-by-line via rolling deque buffer)
    C --> D(Filter out false positive warnings)
    D --> E(Add actual errors to summary)
    B -- No --> F(Parse time & memory metrics from benchmarks)
    F --> G(Format final telemetry report)
    E --> G
    G --> H[pipeline_execution_summary.json]
```

</details>

### 6. `generate_test_data.py` (CI/CD Synthetic Generator)
<details>
<summary>▶ Click to Expand Flowchart</summary>

```mermaid
graph TD
    A[Start] --> B(Build small synthetic genome & GTF annotation)
    B --> C(Generate chrom.sizes & reference FASTA)
    C --> D{STAR on PATH?}
    D -- No --> E[Raise FileNotFoundError]
    D -- Yes --> F(Build STAR genome index)
    F --> G(Simulate paired-end FASTQs from transcript sequences)
```

</details>
