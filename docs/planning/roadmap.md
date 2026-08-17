# Roadmap

**Current status:** MVP v1.0.1 complete.

## Executable MVP — complete

```text
Public Olist data
    ↓
Raw / Bronze Parquet
    ↓
DuckDB
    ↓
Silver
    ↓
Gold
    ↓
Metrics Layer
    ├─ Streamlit BI
    ├─ XGBoost / MLflow
    ├─ FastAPI
    └─ Governed Analytics Agent
    ↓
Integration validation
```

## Future target architecture

Possible future evolution includes:

1. dedicated Data Quality framework;
2. dbt Core;
3. Airflow orchestration;
4. Garage / PostgreSQL runtime;
5. Superset;
6. Prometheus / Grafana / OpenTelemetry;
7. LLM-backed agent orchestration;
8. HITL/action workflows;
9. synthetic operational datasets;
10. broader CI/CD and release automation.

These items are not required for the completed ADR-0009 portfolio MVP.

See `docs/planning/mvp-status.md` for the authoritative implementation matrix.
