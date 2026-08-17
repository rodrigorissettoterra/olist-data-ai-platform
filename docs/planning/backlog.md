# Backlog and Delivery Status

**Current status:** Executable MVP complete
**Current version:** v1.0.1
**Scope authority:** ADR-0009

The original M0–M11 backlog was designed for a broader production-oriented architecture. During implementation, ADR-0009 formally adopted a Windows-native portfolio MVP and removed Docker/WSL-dependent infrastructure from the critical path.

The authoritative current status matrix is:

```text
docs/planning/mvp-status.md
```

## Completed executable MVP

- public Olist source acquisition/import;
- 11-source validation;
- ingestion manifest with SHA-256;
- Bronze Parquet;
- DuckDB warehouse;
- Silver normalized entities;
- Gold facts and dimensions;
- shared Metrics Layer;
- Streamlit BI;
- delivery-delay ML use case;
- leakage-aware temporal split;
- XGBoost model;
- MLflow local tracking;
- persisted model;
- FastAPI serving;
- governed deterministic analytics agent;
- integration suite;
- Ruff validation;
- static GitHub Actions validation;
- final README and architecture documentation.

## Deferred target-architecture capabilities

These items remain valid evolution paths but are **not runtime claims of the MVP**:

- Garage object storage;
- PostgreSQL analytical warehouse;
- Docker Compose runtime;
- Apache Airflow;
- dbt Core;
- dedicated OSS Data Quality platform;
- Apache Superset;
- Prometheus;
- Grafana;
- OpenTelemetry;
- LLM-backed agent orchestration;
- sensitive action workflows / HITL;
- deterministic synthetic inventory and operational-event datasets.

## Historical M0–M11 mapping

The original target roadmap was:

1. M0 Foundation
2. M1 Data Sources & Ingestion
3. M2 Data Lake
4. M3 Data Quality & Engineering
5. M4 Analytics Engineering
6. M5 Business Intelligence
7. M6 Data Science
8. M7 MLOps
9. M8 Agentic AI
10. M9 Observability
11. M10 Feedback & Human-in-the-loop
12. M11 CI/CD & Release

The executable MVP implements the portfolio-relevant capabilities across those areas where listed as complete in `mvp-status.md`; the remaining target components were explicitly deferred by ADR-0009.

## Scope control

A technology is added only when it solves a concrete problem, has a clear responsibility and justifies its operational cost. Future target components do not block the completed portfolio MVP.
