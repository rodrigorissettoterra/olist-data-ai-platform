# Olist Data & AI Platform

> **End-to-end, local-first Data & AI portfolio platform built on public Brazilian e-commerce data.**

![Status](https://img.shields.io/badge/status-MVP%20validated-success)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![DuckDB](https://img.shields.io/badge/Warehouse-DuckDB-yellow)
![ML](https://img.shields.io/badge/ML-XGBoost-orange)
![API](https://img.shields.io/badge/API-FastAPI-009688)
![Tests](https://img.shields.io/badge/integration%20tests-12%20passing-success)

---

## Overview

The **Olist Data & AI Platform** demonstrates how Data Engineering, analytical modeling, Business Intelligence, Machine Learning, MLOps, API serving and governed AI tooling can share the same analytical foundation.

The executable MVP runs locally on Windows without requiring a cloud account, Docker or WSL.

```text
Olist public datasets
        |
        v
       Raw
        |
        v
 Bronze / Parquet
        |
        v
      DuckDB
        |
   +----+----+----------------+
   |         |                |
 Silver    Gold            Metrics
                              |
               +--------------+--------------+
               |              |              |
          Streamlit BI   ML / MLflow     FastAPI
                                             |
                                      Prediction API

                     Metrics / Gold
                           |
                           v
                 Governed Analytics Agent
```

The repository also preserves a broader production-oriented target architecture for future evolution.

---

## What is implemented

The current MVP includes:

- ingestion of 11 source CSV files;
- ingestion metadata and SHA-256 hashes;
- Raw and Bronze layers;
- Snappy-compressed Parquet;
- DuckDB analytical warehouse;
- Silver normalized entities;
- Gold facts and dimensions;
- shared Metrics Layer;
- Streamlit analytical dashboard;
- delivery-delay prediction model;
- temporal Machine Learning evaluation;
- XGBoost;
- MLflow experiment tracking;
- persisted model artifact;
- FastAPI serving;
- prediction endpoint for real orders;
- governed analytical agent;
- limited conversational context;
- automated end-to-end integration tests.

Final validation:

```text
12 passed
```

---

## Data sources

The project uses two public Olist datasets.

### Olist Brazilian E-Commerce Dataset

The platform ingests:

- customers;
- geolocation;
- orders;
- order items;
- payments;
- reviews;
- products;
- sellers;
- product-category translations.

### Olist Marketing Funnel

The platform also ingests:

- marketing qualified leads;
- closed deals.

Total:

```text
11 CSV files
```

External datasets remain subject to their original licenses and terms.

---

## Data architecture

### Bronze

Raw CSV data is converted to Parquet and loaded into the `bronze` schema.

The ingestion process records source metadata and SHA-256 hashes.

### Silver

The normalized analytical layer includes:

- customers;
- orders;
- order items;
- order payments;
- order reviews;
- products;
- sellers;
- geolocation;
- marketing qualified leads;
- closed deals.

### Gold

Current Gold assets include:

```text
gold.dim_customers
gold.dim_products
gold.fact_orders
gold.fact_order_items
```

### Metrics Layer

Current governed analytical outputs include:

```text
metrics.executive_kpis
metrics.monthly_sales
metrics.category_performance
metrics.state_performance
```

BI, API and analytical tools reuse shared metric definitions instead of reimplementing business logic independently.

---

## Metric semantics

### GMV

In this project:

```text
GMV = sum of item prices transacted in the marketplace
```

GMV is **not equivalent to Olist revenue**.

A category may have higher GMV while having fewer orders. Therefore the platform treats financial volume and order count as separate dimensions.

### Number of orders

Order volume is based on distinct `order_id`.

### Payments

Payment totals are maintained separately from GMV because they represent a different business measure.

### Delivery delay

A delivered order is classified as delayed when:

```text
actual delivery date > estimated delivery date
```

---

## Current analytical snapshot

| Metric | Value |
|---|---:|
| Orders | 99,441 |
| Unique customers | 96,096 |
| Delivered orders | 96,478 |
| Canceled orders | 625 |
| GMV | R$ 13,591,643.70 |
| Average order GMV | R$ 136.68 |
| Average review score | 4.09 / 5 |
| Delayed deliveries | 8.11% |
| Average delivery time | 12.5 days |

---

## Business Intelligence

The Streamlit application contains four views:

1. Executive Overview
2. Sales & Customers
3. Operations & Logistics
4. Predictive & AI Insights

Run:

```powershell
.\.venv\Scripts\python.exe -m streamlit run .\dashboard\app.py
```

Then access:

```text
http://localhost:8501
```

---

## Machine Learning

The predictive use case is:

```text
delivery_delay_risk
```

The model estimates the risk of a delivered order exceeding its estimated delivery date.

### Leakage prevention

Only information available before the delivery outcome is used as a feature.

The final split is temporal:

```text
70% training
15% validation
15% test
```

The decision threshold is selected only with the validation set.

### Final test performance

| Metric | Result |
|---|---:|
| ROC AUC | 0.7259 |
| PR AUC | 0.1679 |
| Precision | 0.1470 |
| Recall | 0.5528 |
| F1 | 0.2323 |
| Threshold | 0.42 |
| Test delay rate | 6.61% |

The target is imbalanced. The model is presented as a risk-ranking portfolio use case rather than as a production SLA.

Train:

```powershell
.\.venv\Scripts\python.exe .\ml\src\olist_ml\train_delay_model.py
```

Experiment metadata is tracked locally with MLflow and SQLite.

---

## FastAPI

Start:

```powershell
.\.venv\Scripts\python.exe -m uvicorn olist_api.main:app `
    --app-dir .\api\src `
    --port 8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Available endpoints:

| Endpoint | Description |
|---|---|
| `GET /health` | Runtime health |
| `GET /api/v1/kpis` | Executive metrics |
| `GET /api/v1/model/metrics` | Machine Learning evaluation |
| `GET /api/v1/predict/{order_id}` | Delivery-delay risk |

---

## Governed Analytics Agent

The MVP includes a deterministic analytical agent built over explicit, approved tools.

It is intentionally constrained:

- read-only database access;
- no arbitrary SQL;
- no administrative credentials;
- explicit analytical tools;
- limited conversational context;
- no sensitive actions.

Supported subjects include:

- datasets used;
- executive KPIs;
- categories ranked by GMV;
- categories ranked by number of orders;
- states by GMV;
- highest and lowest delivery-delay rates;
- historical order lookup.

Run:

```powershell
.\.venv\Scripts\python.exe .\agent\src\olist_agent\main.py
```

The current agent is **not presented as an LLM-backed generative agent**.

Its tool layer can later be connected to an LLM without granting unrestricted database access.

---

## Automated validation

The integration suite verifies:

- DuckDB availability;
- Bronze/Silver/Gold/Metrics schemas;
- fact-order uniqueness;
- executive KPI consistency;
- persisted model artifacts;
- ML evaluation metrics;
- agent intent routing;
- conversational ranking context;
- FastAPI health;
- KPI serving;
- ML metric serving;
- real order prediction.

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest `
    .\tests\integration\test_mvp_integration.py `
    -v
```

Validated result:

```text
12 passed
```

The current environment may emit two NumPy/joblib deprecation warnings while loading the persisted model. They do not cause test failures.

---

## Running locally

### 1. Create the environment

```powershell
python -m venv .venv
```

### 2. Install runtime dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install .
```

Development and tests:

```powershell
.\.venv\Scripts\python.exe -m pip install ".[dev]"
```

### 3. Source data

Place the source CSV files under:

```text
data/raw/
```

Generated data, DuckDB files, model artifacts, MLflow data and the virtual environment are excluded from Git.

### 4. Build Bronze

```powershell
.\.venv\Scripts\python.exe .\scripts\data\build_bronze.py
```

### 5. Build Silver, Gold and Metrics

```powershell
.\.venv\Scripts\python.exe .\scripts\data\build_silver_gold.py
```

### 6. Train ML

```powershell
.\.venv\Scripts\python.exe .\ml\src\olist_ml\train_delay_model.py
```

---

## MVP versus target architecture

### Executable MVP

- Python 3.12;
- filesystem;
- Parquet;
- DuckDB;
- Streamlit;
- XGBoost;
- MLflow;
- FastAPI;
- governed analytical tools;
- pytest;
- Ruff.

### Target architecture

The repository retains architecture and scaffolding for future evolution with:

- Docker Compose;
- Garage S3-compatible object storage;
- PostgreSQL;
- dbt Core;
- Apache Airflow;
- Apache Superset;
- Prometheus;
- Grafana;
- OpenTelemetry;
- GitHub Actions;
- LLM-backed agent orchestration;
- broader feedback and human-in-the-loop workflows.

These components are not claimed as implemented in the executable MVP.

See:

```text
docs/adr/0009-adopt-windows-native-mvp.md
```

---

## Engineering principles

- local-first;
- Raw → Bronze → Silver → Gold separation;
- shared metric definitions;
- point-in-time correctness;
- leakage prevention;
- governed AI access;
- read-only analytical tools;
- explicit separation between implemented and planned architecture;
- generated data outside Git;
- automated integration validation;
- architectural decisions recorded with ADRs.

---

## License

Original source code and configuration are licensed under the **Apache License 2.0**.

Original documentation and diagrams are licensed under **Creative Commons Attribution 4.0 (CC BY 4.0)** with attribution to Rodrigo Terra.

External datasets remain subject to their original licenses and terms.

---

## Author

**Rodrigo Terra**

Data & AI professional focused on data platforms, Analytics Engineering, Machine Learning, Generative AI, automation, MLOps and reliable AI systems.

- GitHub: https://github.com/rodrigorissettoterra
- LinkedIn: https://www.linkedin.com/in/rodrigo-rissetto-terra/
