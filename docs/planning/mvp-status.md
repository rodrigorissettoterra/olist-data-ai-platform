# MVP v1.0.1 — Implementation Status

**Status:** Complete  
**Scope authority:** ADR-0009  
**Runtime:** Windows-native / local-first

This document is the current implementation-status matrix. Earlier M0–M11 planning documents describe the original target architecture and should be read together with ADR-0009.

| Capability | MVP status | Evidence / implementation |
|---|---|---|
| Public Olist data sources | Implemented | 11 expected CSV files |
| Controlled acquisition helper | Implemented | `scripts/data/download_olist.py` |
| Ingestion metadata / SHA-256 | Implemented | `meta.ingestion_manifest` |
| Bronze / Parquet | Implemented | `scripts/data/build_bronze.py` |
| DuckDB warehouse | Implemented | `data/warehouse/olist.duckdb` |
| Silver layer | Implemented | `scripts/data/build_silver_gold.py` |
| Gold facts/dimensions | Implemented | `gold.*` |
| Shared Metrics Layer | Implemented | `metrics.*` |
| Streamlit BI | Implemented | `dashboard/app.py` |
| Delivery-delay ML | Implemented | XGBoost pipeline |
| Temporal ML validation | Implemented | 70/15/15 split |
| MLflow tracking | Implemented | local SQLite tracking |
| FastAPI serving | Implemented | four documented endpoints |
| Governed analytics agent | Implemented | deterministic, read-only tools |
| Integration validation | Implemented | 12 tests passing locally |
| Ruff validation | Implemented | clean local validation |
| GitHub Actions | Implemented | static repository checks |
| Dedicated Data Quality platform | Deferred | core contracts covered by tests |
| Airflow | Deferred | target architecture |
| dbt Core | Deferred | target architecture |
| Superset | Deferred | Streamlit used in MVP |
| Garage / PostgreSQL runtime | Deferred | DuckDB/filesystem used in MVP |
| Prometheus / Grafana / OTel | Deferred | target architecture |
| LLM-backed agent | Deferred | deterministic agent used in MVP |
| Sensitive action execution / HITL | Deferred | MVP performs no sensitive actions |
| Synthetic datasets | Deferred | real Olist data used in MVP |

## Completion statement

The repository is complete for the **ADR-0009 executable portfolio MVP**.

It is not presented as a complete implementation of every component in the original production-oriented target architecture. Those components are retained as documented evolution paths.
