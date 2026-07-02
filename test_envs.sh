#!/usr/bin/env bash
set -euo pipefail

# Detect conda executable dynamically
CONDA_EXEC=$(which conda 2>/dev/null || which mamba 2>/dev/null || echo "/home/himanshu/miniconda3/bin/conda")

ENVS=(
  rules/envs/star.yaml
  rules/envs/picard.yaml
  rules/envs/fastp.yaml
  rules/envs/deseq2.yaml
  rules/envs/subread.yaml
  rules/envs/python.yaml
  rules/envs/rseqc.yaml
  rules/envs/fastqc.yaml
  rules/envs/preseq.yaml
  rules/envs/multiqc.yaml
  rules/envs/samtools.yaml
  envs/main.yaml
)

PASS=()
FAIL=()
ENV_NAME="__env_test_tmp__"
LOG_FILE="env_test_tmp.log"

# Cleanup trap to ensure the temp log and test env are always removed on exit
cleanup() {
  rm -f "$LOG_FILE"
  "$CONDA_EXEC" env remove -n "$ENV_NAME" -y 2>/dev/null || true
}
trap cleanup EXIT

for yaml in "${ENVS[@]}"; do
  echo "==> Testing: $yaml"
  # Clean up any leftover env from previous run
  "$CONDA_EXEC" env remove -n "$ENV_NAME" -y 2>/dev/null || true

  if "$CONDA_EXEC" env create -n "$ENV_NAME" -f "$yaml" 2>&1 | tee "$LOG_FILE"; then
    echo "    PASS"
    PASS+=("$yaml")
    "$CONDA_EXEC" env remove -n "$ENV_NAME" -y 2>/dev/null || true
  else
    ERR=$(tail -5 "$LOG_FILE" | tr '\n' ' ')
    echo "    FAIL: $ERR"
    FAIL+=("$yaml|||$ERR")
    "$CONDA_EXEC" env remove -n "$ENV_NAME" -y 2>/dev/null || true
  fi
done

echo ""
echo "===== RESULTS ====="
echo "PASSED: ${#PASS[@]}"
echo "FAILED: ${#FAIL[@]}"

if [ ${#FAIL[@]} -gt 0 ]; then
  echo ""
  echo "| File | Error |"
  echo "|------|-------|"
  for entry in "${FAIL[@]}"; do
    file="${entry%%|||*}"
    err="${entry##*|||}"
    echo "| $file | $err |"
  done
fi
