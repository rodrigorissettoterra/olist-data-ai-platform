# Backlog M0–M11

**Status:** Approved v1.0

## M0 — Foundation

- Project Charter — DONE
- Arquitetura v1 — DONE
- Estrutura do repositório — DONE
- Estratégia de armazenamento — DONE
- Catálogo das fontes — DONE
- Convenções — DONE
- ADRs iniciais — DONE
- `.gitignore`, `.env.example`, `.gitattributes` — DONE
- Docker Compose Foundation — materializado, validação operacional pendente
- bootstrap Foundation — materializado, validação operacional pendente
- README — DONE
- licenciamento — materializado
- backlog — DONE
- Definition of Done — DONE

Gate: PostgreSQL/Garage healthy, buckets provisionados, secrets fora do Git,
checks aprovados e working tree coerente.

## M1 — Data Sources & Ingestion

- aquisição/importação controlada;
- source manifest;
- validação pré-ingestão;
- framework de ingestão;
- Raw ingestion;
- idempotência;
- ingestion metadata;
- Airflow foundation;
- DAG de ingestão;
- testes.

Saída: fontes → Raw imutável + metadata por execução segura.

## M2 — Data Lake

- framework Bronze;
- schema handling;
- naming normalization;
- Bronze para fontes reais;
- DuckDB;
- layout de objetos;
- incrementalidade quando fizer sentido;
- framework sintético;
- inventory snapshots;
- operational events;
- testes de lake.

Saída: Raw/Bronze reproduzíveis e consultáveis.

## M3 — Data Quality & Engineering

- decisão final de ferramenta OSS de qualidade;
- profiling;
- baselines;
- checks Raw/Bronze;
- cardinalidades;
- design Silver;
- transforms Silver;
- geolocation consolidation;
- quality reports;
- failure policies.

Saída: Silver confiável e automatizadamente validado.

## M4 — Analytics Engineering

- dbt foundation;
- roles/schemas;
- sources;
- staging;
- intermediate;
- dimensional model;
- facts;
- dimensions;
- marts;
- tests;
- docs/lineage;
- decisão da Metrics Layer;
- Metrics Layer v1;
- reconciliation tests.

Saída: Silver → dbt → Gold → Metrics Layer.

## M5 — BI

- Superset foundation;
- read-only role;
- arquitetura de dashboards;
- Executive Overview;
- Sales & Customers;
- Operations & Logistics;
- shell de Predictive & AI Insights;
- dashboard-as-code;
- validação de KPI;
- performance.

## M6 — Data Science

- ML problem contract;
- leakage analysis;
- feature dataset;
- split temporal;
- baseline;
- feature engineering;
- candidate models;
- evaluation;
- threshold analysis;
- explainability;
- error analysis;
- model card;
- forecast de demanda apenas se agregar valor.

## M7 — MLOps

- MLflow;
- database;
- credencial S3 específica;
- tracking;
- lifecycle de artefato/modelo;
- training pipeline;
- evaluation gate;
- FastAPI;
- prediction endpoint;
- schema validation;
- prediction logging;
- integration tests.

## M8 — Agentic AI

- arquitetura do Agent;
- decisão de framework;
- modelo local;
- Metrics Tool;
- Gold Query Tool;
- Prediction Tool;
- Diagnostic Tool;
- evidence contract;
- query safety;
- Agent API;
- prompt versioning;
- guardrails;
- evaluation.

## M9 — Observability

- Prometheus;
- Grafana;
- OTel Collector;
- instrumentation;
- pipeline metrics;
- Data Quality metrics;
- ML metrics;
- Agent metrics;
- dashboards operacionais;
- alert rules;
- tracing.

## M10 — Feedback & Human-in-the-loop

- classificação de ações;
- action proposal schema;
- approval workflow;
- persistence;
- Action Tool;
- audit log;
- feedback capture;
- feedback analytics;
- safety tests.

## M11 — CI/CD & Release

- pre-commit;
- Python CI;
- dbt CI;
- Data Quality CI;
- Docker validation;
- security checks;
- contract tests;
- integration CI;
- E2E smoke test;
- docs checks;
- release workflow;
- final bootstrap;
- portfolio evidence;
- documentação final.

## Controle de escopo

Nova tecnologia só entra quando resolve problema real, possui responsabilidade
clara e trade-off justificável. Itens opcionais não bloqueiam milestones.
