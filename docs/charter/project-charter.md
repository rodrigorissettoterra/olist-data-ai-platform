# Project Charter — olist-data-ai-platform

**Status:** Approved vision; executable MVP delivered under ADR-0009
**Author:** Rodrigo Terra

## Active delivery note

The original charter defined a broad production-oriented target architecture. During implementation, ADR-0009 formally narrowed the executable portfolio MVP to a Windows-native local-first runtime.

Therefore:

- the **vision** below remains the long-term architecture direction;
- the **implemented MVP** is the scope defined by ADR-0009;
- unimplemented target components are documented as future evolution and are not presented as current runtime capabilities.

Current implementation status: `docs/planning/mvp-status.md`.

## Vision

Build an end-to-end Data & AI platform over a realistic Brazilian e-commerce scenario, capable of transforming raw data into reliable information, operational predictions and governed analytical decision support.

## Core problem

Transform e-commerce data into a platform capable of:

1. explaining historical performance;
2. identifying operational patterns;
3. predicting delivery risk;
4. exposing consistent metrics;
5. supporting governed analytical questions;
6. serving analytics and predictions through explicit interfaces.

## Executable MVP architecture

```text
Sources → Raw/Bronze → DuckDB → Silver → Gold → Metrics
                                  ├─ BI
                                  ├─ ML / MLflow
                                  ├─ FastAPI
                                  └─ Governed Analytics Agent
```

## Real sources

- Olist Brazilian E-Commerce Dataset
- Olist Marketing Funnel

## BI

Implemented views:

- Executive Overview
- Sales & Customers
- Operations & Logistics
- Predictive & AI Insights

## Main ML use case

`delivery_delay_risk`

The prediction contract is point-in-time aware; delivery outcome fields are not used as model features.

## Agent

The executable MVP uses a deterministic governed analytics agent with read-only data access and explicit analytical intents.

LLM orchestration, recommendations that trigger actions and human-in-the-loop execution remain future target capabilities.

## Constraints

1. Core execution remains local-first.
2. No essential MVP function depends on a paid cloud service or trial.
3. Large data, generated artifacts and secrets do not enter Git.
4. Architecture and implementation claims must remain explicit and auditable.
5. Security, maintenance and reproducibility take priority over unnecessary infrastructure complexity.

## Target architecture retained for evolution

The broader reference stack remains:

Git/GitHub, Docker Compose, Garage, PostgreSQL, DuckDB, dbt Core, Airflow, a dedicated OSS Data Quality solution, Superset, scikit-learn/XGBoost, MLflow, FastAPI, local/Hugging Face models, Prometheus, Grafana, OpenTelemetry and GitHub Actions.

Only the components identified as implemented in `docs/planning/mvp-status.md` are runtime claims of the current MVP.

## Success criterion

The executable MVP succeeds when a reproducible chain takes public Olist sources through analytical layers to BI, ML, serving and governed analytics, with automated validation and faithful documentation.

## Guiding principle

> The platform should look like a professional system reduced to portfolio scale, not a collection of disconnected technology demonstrations.
