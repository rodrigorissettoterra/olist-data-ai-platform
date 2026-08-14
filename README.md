# olist-data-ai-platform

> Plataforma Data & AI end-to-end, local-first, para análise, previsão e decisão
> assistida por IA usando dados públicos da Olist.

**Status atual:** M0 — Foundation
**Autor:** Rodrigo Terra

## Objetivo

Construir uma plataforma profissional de portfólio capaz de transformar dados
brutos de e-commerce em dados confiáveis, métricas governadas, dashboards,
previsões e investigação assistida por Agentic AI.

```text
Sources → Ingestion → Raw/Bronze → Data Quality → Silver
        → Analytics Engineering → Gold → Metrics Layer
        → BI / ML / Agent → Serving → Observability → Feedback
```

O projeto é deliberadamente local-first: nenhuma conta AWS, GCP, Azure ou outro
serviço cloud é necessária para executar o núcleo da plataforma.

## Fontes

Fontes reais obrigatórias:

- Olist Brazilian E-Commerce Dataset
- Olist Marketing Funnel

Fontes sintéticas derivadas e reproduzíveis:

- inventory snapshots
- operational events

Campaigns e web events permanecem opcionais.

## Stack planejada

| Responsabilidade | Tecnologia |
|---|---|
| Versionamento | Git + GitHub |
| Runtime local | Docker Compose |
| Object storage / Data Lake | Garage |
| Warehouse | PostgreSQL |
| Analytics local | DuckDB |
| Analytics Engineering | dbt Core |
| Orquestração | Apache Airflow |
| Data Quality | OSS a confirmar por ADR |
| BI | Apache Superset |
| ML | scikit-learn / XGBoost |
| Tracking e artefatos | MLflow self-hosted |
| Serving | FastAPI |
| Agentic AI | modelos locais / Hugging Face |
| Métricas | Prometheus |
| Monitoring | Grafana OSS |
| Telemetry | OpenTelemetry |
| CI/CD | GitHub Actions |

## Data Lake

Garage fornece o endpoint S3-compatible local.

Buckets aprovados:

- `olist-raw`
- `olist-bronze`
- `olist-silver`
- `olist-gold`
- `olist-ml`

Compatibilidade S3 é uma abstração técnica. AWS não faz parte do runtime do
projeto.

## BI obrigatório

A versão final deverá incluir:

1. Executive Overview
2. Sales & Customers
3. Operations & Logistics
4. Predictive & AI Insights

BI, API analítica e Agent devem reutilizar a mesma Metrics Layer.

## Machine Learning

O primeiro caso de ML será `delivery_delay_risk`.

Features somente poderão utilizar informação disponível no instante formal da
previsão. Variáveis posteriores ao resultado serão proibidas para evitar
leakage.

## Agent

O Agent deverá consultar Metrics Layer, Gold e predictions por tools governadas.
Ele não terá credenciais administrativas.

Ações sensíveis seguem:

```text
READ → automático
ANALYZE → automático
RECOMMEND → automático
PROPOSE ACTION → automático
EXECUTE SENSITIVE ACTION → aprovação humana obrigatória
```

## Foundation

M0 ativa apenas:

- PostgreSQL
- Garage

Os demais serviços entram somente em seus milestones.

### Bootstrap

No PowerShell, a partir da raiz do repositório:

```powershell
python .\scripts\bootstrap\bootstrap_foundation.py
```

O script cria o `.env`, gera os secrets da Foundation, valida Docker Compose,
sobe PostgreSQL e Garage, aguarda os healthchecks, garante os buckets e aplica
as permissões iniciais do pipeline.

### Validação estática

```powershell
python .\scripts\bootstrap\validate_m0.py
```

## Roadmap

- M0 Foundation
- M1 Data Sources & Ingestion
- M2 Data Lake
- M3 Data Quality & Engineering
- M4 Analytics Engineering
- M5 BI
- M6 Data Science
- M7 MLOps
- M8 Agentic AI
- M9 Observability
- M10 Feedback & Human-in-the-loop
- M11 CI/CD & Release

Consulte `docs/planning/backlog.md`.

## Documentação

- `docs/charter/project-charter.md`
- `docs/architecture/architecture-v1.md`
- `docs/data/source-catalog.md`
- `docs/data/storage-strategy.md`
- `docs/conventions/`
- `docs/adr/`
- `docs/planning/`

## Licença

Código e configurações originais deste projeto: Apache License 2.0.

Documentação e diagramas originais: CC BY 4.0, com atribuição a Rodrigo Terra.

Datasets externos permanecem sujeitos aos termos de suas fontes originais.

## Estado real

M0 está materializado neste pacote. Ingestão, Bronze/Silver, dbt, dashboards,
ML, MLflow, API, Agent e observabilidade **ainda não estão implementados** e só
serão iniciados após o gate operacional do M0.
