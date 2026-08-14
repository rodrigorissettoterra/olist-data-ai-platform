# Project Charter — olist-data-ai-platform

**Status:** Approved v1.0
**Milestone:** M0 — Foundation
**Autor:** Rodrigo Terra

## Visão

Construir uma plataforma Data & AI end-to-end sobre um cenário realista de
e-commerce brasileiro, capaz de transformar dados brutos em informação
confiável, previsões operacionais e suporte inteligente à decisão.

O projeto deve demonstrar Data Engineering, Analytics Engineering, Data
Quality, BI, Data Science, ML Engineering, MLOps, API/Serving, Agentic AI,
observabilidade, governança técnica e CI/CD.

## Problema central

Transformar dados brutos de e-commerce em uma plataforma confiável capaz de:

1. explicar desempenho histórico;
2. identificar problemas e possíveis causas;
3. prever riscos futuros;
4. disponibilizar métricas consistentes;
5. apoiar decisões por IA;
6. observar dados, pipelines, modelos e serviços;
7. incorporar feedback humano.

## Arquitetura aprovada

```text
Fontes → Ingestão → Raw/Bronze → Data Quality → Silver
       → Analytics Engineering → Gold → Metrics Layer
       → BI / ML / Agent → Serving → Observability → Feedback
```

## Fontes

### Reais

- Olist Brazilian E-Commerce Dataset
- Olist Marketing Funnel

### Sintéticas derivadas

Obrigatórias:
- inventory snapshots;
- operational events.

Opcionais:
- campaigns;
- web events.

Dados sintéticos devem ser determinísticos, reproduzíveis, versionados por
código e inequivocamente identificados como sintéticos.

## BI obrigatório

- Executive Overview
- Sales & Customers
- Operations & Logistics
- Predictive & AI Insights

Dashboard e Agent devem consumir a mesma Metrics Layer.

## ML principal

`delivery_delay_risk`.

O instante da previsão será formalmente definido antes do treinamento. Nenhuma
feature poderá utilizar informação indisponível nesse instante.

## Agent

Deve investigar métricas, consultar Gold e modelos, explicar causas, recomendar
ações e utilizar human-in-the-loop para ações sensíveis.

## Restrições obrigatórias

1. Apenas OSS, gratuito ou free tier permanente suficiente.
2. Nenhuma função essencial pode depender de trial.
3. O núcleo deve continuar funcional localmente.
4. Código, SQL, pipelines, configs, BI, ML, Agent, testes e docs devem ser
   produzidos de forma reproduzível.
5. A atuação manual deve ser reduzida ao inevitável.
6. Priorizar provisioning por código, scripts e imports.
7. Segurança, manutenção e reprodutibilidade; sem gambiarras.
8. Dados grandes e secrets não entram no Git.

## Stack de referência

Git/GitHub, Docker Compose, Garage, PostgreSQL, DuckDB, dbt Core, Airflow,
solução OSS de Data Quality, Superset, scikit-learn/XGBoost, MLflow, FastAPI,
modelos locais/Hugging Face, Prometheus, Grafana OSS, OpenTelemetry e GitHub
Actions.

## Local-first

AWS, GCP, Azure e outros clouds não fazem parte do runtime obrigatório.
Compatibilidade S3 existe para portabilidade, não como dependência AWS.

## Critério de sucesso

Ao final, uma cadeia integrada deve levar fontes reais/sintéticas a Raw,
camadas tratadas, Gold, métricas, BI, ML, Agent, serving, observabilidade,
feedback e CI/CD, com lineage, testes e documentação.

## Princípio orientador

> A plataforma deve parecer um sistema profissional reduzido à escala de um
> projeto de portfólio, e não uma coleção de ferramentas conectadas apenas
> para demonstrar tecnologias.
