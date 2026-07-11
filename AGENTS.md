# Agent Entrypoint

This is a production-grade bulk RNA-seq pipeline built with Snakemake 8.0+.

## Navigation Map

* **Pipeline Overview & Quick Start**: [README.md](README.md)
* **Snakemake Rules & DAG**: [rules/README.md](rules/README.md)
* **Python Scripts & Flowcharts**: [rules/scripts/README.md](rules/scripts/README.md)
* **Execution Profiles (Local / SLURM / Cloud)**: [profiles/README.md](profiles/README.md)
* **Bash Wrappers**: [scripts/README.md](scripts/README.md)
* **Conda Environments (Grouped)**: [envs/README.md](envs/README.md)
* **Conda Environments (Modular, per-rule)**: [rules/envs/README.md](rules/envs/README.md)
* **Living Wiki**: [openwiki/](openwiki/) (auto-updated via [.github/workflows/openwiki-update.yml](.github/workflows/openwiki-update.yml))
* **Knowledge Graph**: [graphify-out/](graphify-out/) (run `graphify query "<question>"` to explore)

## Codebase Exploration

**Graphify** (preferred for targeted questions):
* `graphify query "<question>"` — Search the knowledge graph.
* `graphify path "<A>" "<B>"` — Find relationships between two concepts.
* `graphify explain "<concept>"` — Deep dive into a specific concept.
* `graphify update .` — Rebuild the graph after code changes.

**Understand-Anything** (for broad architecture scans):
* `understand` — Build `.understand-anything/knowledge-graph.json`.
* `understand-dashboard` — Launch the interactive React dashboard.
* `understand-chat` — Query the knowledge graph.
* `understand-diff` / `understand-explain` — Inspect diffs or individual modules.
