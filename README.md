# Olist Data & AI Platform

> **An end-to-end, local-first Data & AI platform designed to transform raw e-commerce data into trusted analytics, predictions, and AI-assisted decisions.**

This project is a professional Data & AI engineering portfolio platform built around public **Olist Brazilian E-Commerce** data.

Its objective is to demonstrate how multiple disciplines can work together in one governed architecture:

**Data Engineering → Data Quality → Analytics Engineering → BI → Data Science → MLOps → Agentic AI → Observability → Feedback**

<p>
  <img src="https://img.shields.io/badge/Status-M0%20Foundation-blue" alt="M0 Foundation">
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white" alt="Docker Compose">
  <img src="https://img.shields.io/badge/PostgreSQL-Warehouse-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Data%20%26%20AI-End--to--End-purple" alt="Data & AI">
  <img src="https://img.shields.io/badge/Architecture-Local--First-green" alt="Local First">
</p>

---

## Current status

### M0 — Foundation

The project is intentionally developed through gated milestones rather than presenting planned components as already implemented.

### Implemented in the repository

- project charter and architectural foundation;
- repository structure and conventions;
- Docker Compose foundation;
- PostgreSQL foundation configuration;
- Garage S3-compatible object-storage foundation;
- environment template and configuration conventions;
- bootstrap automation;
- static M0 validation;
- storage strategy;
- source catalog;
- ADRs and architectural decisions;
- licensing model;
- milestone backlog from M0 to M11.

### Planned for later milestones

- production ingestion pipelines;
- Bronze / Silver / Gold data processing;
- formal Data Quality layer;
- dbt analytical models;
- Airflow orchestration;
- governed Metrics Layer;
- Superset dashboards;
- Machine Learning models;
- MLflow tracking and artifacts;
- FastAPI serving;
- Agentic AI;
- Prometheus / Grafana / OpenTelemetry observability;
- feedback and human-in-the-loop workflows;
- final CI/CD release workflow.

This distinction is deliberate: **the README reflects the real implementation state of the project.**

---

## The problem

E-commerce data is naturally fragmented across customers, orders, products, sellers, payments, reviews, logistics, marketing funnels, inventory, and operational events.

A useful analytical system must do more than load these tables.

It must answer questions such as:

- Can the data be trusted?
- Which metrics have a single governed definition?
- Why is performance changing?
- Which orders are likely to be delayed?
- Which customers or operational areas deserve attention?
- Can an AI assistant investigate data without bypassing governance?
- Can the complete system be reproduced locally?

This project is designed to answer those questions as one integrated platform.

---

## Target architecture

```text
Sources
   ↓
Ingestion
   ↓
Raw / Bronze
   ↓
Data Quality
   ↓
Silver
   ↓
Analytics Engineering
   ↓
Gold
   ↓
Metrics Layer
   ↓
┌───────────────┬───────────────┬───────────────┐
│      BI       │      ML       │     Agent     │
└───────────────┴───────────────┴───────────────┘
                         ↓
                       Serving
                         ↓
                    Observability
                         ↓
                       Feedback
```

The key principle is that BI, predictive models, APIs, and AI agents should consume **governed analytical assets**, rather than independently rebuilding business logic.

---

## Why local-first

The core platform is designed to run without requiring an AWS, GCP, or Azure account.

This has several goals:

- make the project reproducible;
- make infrastructure visible rather than abstracted away;
- keep experimentation economically accessible;
- demonstrate architecture rather than cloud-vendor dependence;
- preserve portable interfaces such as S3-compatible object storage.

Local-first does **not** mean cloud-incompatible. The architecture deliberately uses patterns that can later be mapped to managed cloud services.

---

## Data sources

### Real public sources

- **Olist Brazilian E-Commerce Dataset**
- **Olist Marketing Funnel**

### Reproducible synthetic sources

- inventory snapshots;
- operational events.

Campaign and web-event sources remain optional extensions.

External datasets remain subject to their original licenses and terms.

---

## Planned technology stack

| Responsibility | Technology |
|---|---|
| Version control | Git + GitHub |
| Local runtime | Docker Compose |
| Object storage / Data Lake | Garage |
| Warehouse | PostgreSQL |
| Local analytics | DuckDB |
| Analytics Engineering | dbt Core |
| Orchestration | Apache Airflow |
| Data Quality | OSS solution to be finalized by ADR |
| BI | Apache Superset |
| Machine Learning | scikit-learn / XGBoost |
| Experiment tracking | MLflow self-hosted |
| Serving | FastAPI |
| Agentic AI | Local / open models and governed tools |
| Metrics | Prometheus |
| Monitoring | Grafana OSS |
| Telemetry | OpenTelemetry |
| CI/CD | GitHub Actions |

A technology appearing in this table does not imply that it is already implemented. Components are introduced only in their approved milestones.

---

## Data Lake strategy

Garage provides the local S3-compatible object-storage interface.

Approved buckets:

```text
olist-raw
olist-bronze
olist-silver
olist-gold
olist-ml
```

S3 compatibility is treated as a **technical interface**, not as a dependency on AWS.

---

## Analytics Engineering and Metrics Layer

The platform is designed so that business metrics are not independently recreated by every consumer.

```text
Silver / Gold
     ↓
Governed Metrics Layer
     ↓
BI + API + ML + Agent
```

This should reduce metric drift and make analytical definitions easier to audit, test, and reuse.

---

## Business Intelligence

The final BI layer is planned around four views:

1. **Executive Overview**
2. **Sales & Customers**
3. **Operations & Logistics**
4. **Predictive & AI Insights**

Dashboards should consume the same governed metric definitions used by analytical APIs and AI tools.

---

## Machine Learning

The first planned predictive use case is:

```text
delivery_delay_risk
```

A central modeling rule is **point-in-time correctness**.

Only information available at the formal prediction timestamp may be used as a feature. Variables that become available after the target event are prohibited to prevent leakage.

The planned ML lifecycle includes:

```text
Features
   ↓
Training
   ↓
Evaluation
   ↓
MLflow Tracking
   ↓
Model Artifact
   ↓
Serving
   ↓
Monitoring
   ↓
Feedback
```

---

## Agentic AI governance

The future agent will not receive unrestricted database access or administrative credentials.

It is designed to consume governed tools over approved analytical assets such as the Metrics Layer, Gold models, and prediction outputs.

The action model is:

```text
READ                     → automatic
ANALYZE                  → automatic
RECOMMEND                → automatic
PROPOSE ACTION           → automatic
EXECUTE SENSITIVE ACTION → human approval required
```

The agent is intended to support investigation and decision-making without becoming an uncontrolled privileged actor.

---

## M0 Foundation

The current milestone establishes only the minimum infrastructure required before data ingestion begins.

Foundation services:

- PostgreSQL;
- Garage.

Later services are introduced only when their milestone starts.

### Bootstrap

From the repository root on PowerShell:

```powershell
python .\scripts\bootstrap\bootstrap_foundation.py
```

The bootstrap workflow is designed to:

- create `.env` when required;
- generate Foundation secrets;
- validate Docker Compose configuration;
- start PostgreSQL and Garage;
- wait for health checks;
- create the approved buckets;
- apply initial pipeline permissions.

### Static validation

```powershell
python .\scripts\bootstrap\validate_m0.py
```

---

## Roadmap

| Milestone | Scope |
|---|---|
| **M0** | Foundation |
| **M1** | Data Sources & Ingestion |
| **M2** | Data Lake |
| **M3** | Data Quality & Engineering |
| **M4** | Analytics Engineering |
| **M5** | Business Intelligence |
| **M6** | Data Science |
| **M7** | MLOps |
| **M8** | Agentic AI |
| **M9** | Observability |
| **M10** | Feedback & Human-in-the-loop |
| **M11** | CI/CD & Release |

The detailed backlog is maintained in [`docs/planning/backlog.md`](docs/planning/backlog.md).

---

## Documentation-first engineering

Architectural and product decisions are kept outside implementation code whenever they represent contracts or long-lived design choices.

Key documentation areas include:

- [`docs/charter/project-charter.md`](docs/charter/project-charter.md)
- [`docs/architecture/architecture-v1.md`](docs/architecture/architecture-v1.md)
- [`docs/data/source-catalog.md`](docs/data/source-catalog.md)
- [`docs/data/storage-strategy.md`](docs/data/storage-strategy.md)
- [`docs/conventions/`](docs/conventions/)
- [`docs/adr/`](docs/adr/)
- [`docs/planning/`](docs/planning/)

ADRs are used to record architectural choices so that important trade-offs remain explicit and reviewable.

---

## Engineering principles

### Build in milestones

New infrastructure is added only when a milestone requires it.

### Separate implemented from planned

The repository should never imply that roadmap components already exist.

### Govern metrics once

BI, ML, APIs, and Agentic AI should reuse common analytical definitions.

### Prevent leakage by design

Predictive features must respect the formal prediction point in time.

### Restrict AI privileges

Agents should operate through governed tools and require human approval for sensitive actions.

### Observe the complete system

The target architecture treats data pipelines, models, APIs, and agents as observable production components rather than isolated experiments.

---

## License

Original source code and configuration are licensed under the **Apache License 2.0**.

Original documentation and diagrams are licensed under **Creative Commons Attribution 4.0 (CC BY 4.0)** with attribution to Rodrigo Terra.

External datasets remain subject to the licenses and terms of their original sources.

---

## Author

**Rodrigo Terra**

Data & AI professional focused on analytics engineering, data platforms, Machine Learning, Generative AI, automation, MLOps, and reliable AI systems.

- GitHub: [@rodrigorissettoterra](https://github.com/rodrigorissettoterra)
- LinkedIn: [Rodrigo Terra](https://www.linkedin.com/in/rodrigo-rissetto-terra/)