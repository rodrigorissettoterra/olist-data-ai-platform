# Arquitetura v1 — olist-data-ai-platform

**Status:** Approved v1.0
**Milestone:** M0 — Foundation

## Arquitetura lógica

```text
Sources
  ↓
Ingestion
  ↓
Raw
  ↓
Bronze
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
  ├── BI
  ├── ML
  └── Agent
       ↓
     Serving
       ↓
 Observability
       ↓
   Feedback
```

A arquitetura não é estritamente linear: metadata, quality, observability,
experiment tracking e feedback são fluxos transversais.

## Responsabilidades

### Garage

Object storage S3-compatible local:

- Raw
- Bronze
- Silver
- Gold file-based
- feature datasets
- ML artifacts

### PostgreSQL

- warehouse;
- facts/dimensions/marts;
- Metrics Layer relacional;
- metadata da plataforma;
- estado relacional de componentes quando apropriado.

Metadata interna de Airflow, Superset e MLflow usará databases separados.

### DuckDB

Engine analítica local para Parquet, profiling, validação e processamento. Não
é o warehouse central.

### dbt Core

Analytics Engineering:

```text
sources → staging → intermediate → marts → metrics
```

### Airflow

Orquestração. DAGs coordenam; lógica pesada permanece em módulos testáveis.

### BI

Superset consome Gold/Metrics em PostgreSQL.

### ML/MLOps

```text
Gold → Feature Dataset → Training → Evaluation → MLflow
     → Approved Model → FastAPI → Prediction
```

### Agent

```text
User → Agent → governed tools
             ├── Metrics Tool
             ├── Gold Query Tool
             ├── Prediction Tool
             └── Action Tool
```

O Agent não acessa Raw diretamente nem possui credenciais administrativas.

### HITL

```text
READ                 automatic
ANALYZE              automatic
RECOMMEND            automatic
PROPOSE ACTION       automatic
EXECUTE SENSITIVE    human approval required
```

## Observabilidade

Stack prevista:

- Prometheus;
- Grafana OSS;
- OpenTelemetry.

Cobertura futura: infraestrutura, serviços, pipelines, Data Quality, ML e Agent.

## CI/CD

GitHub Actions deverá validar lint, tests, dbt, configs, containers, contracts,
segurança e documentação nos milestones apropriados.

## Princípios

1. Local-first
2. Reprodutível
3. Lineage rastreável
4. Single source of truth para KPIs
5. Separation of concerns
6. Observable
7. Testable
8. Secure by default
9. No hidden manual state
10. Portfolio realism

## Decisões fechadas

- Raw → Bronze → Silver → Gold.
- Garage como object storage S3-compatible.
- PostgreSQL como warehouse/marts.
- DuckDB como engine analítica local.
- Parquet como formato analítico do lake.
- dbt para Analytics Engineering.
- Airflow para orquestração.
- Superset para BI.
- MLflow self-hosted para lifecycle de ML.
- FastAPI para serving.
- Prometheus/Grafana/OpenTelemetry para observabilidade.
- Docker Compose para runtime local.
- GitHub Actions para CI/CD.
- Metrics Layer compartilhada.
- Agent por tools governadas.
- HITL para ações sensíveis.
- Raw imutável.
- dados grandes fora do Git.

## Decisões abertas

- ferramenta final de Data Quality;
- implementação exata da Metrics Layer;
- particionamento por dataset;
- estratégia incremental;
- modelo dimensional final;
- framework do Agent;
- modelo local;
- estratégia detalhada de logs/drift/feedback.

Essas decisões só serão fechadas quando houver contexto técnico suficiente.
