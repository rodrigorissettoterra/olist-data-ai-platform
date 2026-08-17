# Definition of Done

**Status:** Approved for executable MVP
**Scope authority:** ADR-0009

## General rule

> Done means implemented, validated, reproducible, documented and coherent with the active architecture.

A task is not complete merely because code exists.

## Executable MVP completion gate

The ADR-0009 MVP is considered complete when all applicable items below are satisfied:

1. public source files can be acquired or placed under `data/raw/`;
2. all 11 expected CSV files are validated before Bronze build;
3. ingestion metadata includes row count, size and SHA-256;
4. Bronze Parquet and DuckDB tables build successfully;
5. Silver, Gold and Metrics layers build successfully;
6. `gold.fact_orders` preserves one row per order;
7. BI consumes governed analytical tables;
8. ML uses a leakage-aware prediction contract;
9. ML split is temporal and threshold selection does not use test data;
10. model metrics and model bundle are persisted;
11. FastAPI exposes health, KPI, model-metric and prediction endpoints;
12. analytics agent uses read-only governed queries and no arbitrary SQL;
13. integration tests pass;
14. Ruff passes;
15. generated datasets, model artifacts, databases and secrets are outside Git;
16. documentation distinguishes implemented MVP components from target architecture;
17. screenshots/visual documentation represent real implemented components.

## Current evidence

- 12 integration tests pass locally;
- final delivery-delay test ROC AUC: 0.7257;
- Streamlit dashboard validated locally;
- FastAPI Swagger validated locally;
- agent ranking/context behavior validated locally;
- GitHub repository contains the source, ADRs and reproducibility instructions.

## Data

- Source provenance is explicit.
- SHA-256 is preserved in ingestion metadata.
- Gold fact grain is tested.
- Multi-grain monetary joins are handled through explicit aggregation.
- GMV and payments are separate measures.
- Synthetic data is not presented as observed data.

## Machine Learning

A model requires:

- problem statement;
- target and prediction point;
- leakage analysis;
- temporal evaluation where applicable;
- baseline/evaluation evidence;
- threshold policy;
- deterministic random seed;
- persisted artifact and metrics.

## Agent

The current MVP agent must:

- use explicit tools/intents;
- access DuckDB read-only;
- avoid arbitrary SQL;
- avoid administrative credentials;
- perform no sensitive actions;
- distinguish GMV from order count.

LLM orchestration and HITL are target-architecture capabilities, not current MVP requirements.

## Target infrastructure

Docker Compose, Garage, PostgreSQL, Airflow, dbt, Superset and the complete observability stack are retained as future architecture components.

Their original M0-specific gate is historical and does not supersede ADR-0009 for the executable MVP.
