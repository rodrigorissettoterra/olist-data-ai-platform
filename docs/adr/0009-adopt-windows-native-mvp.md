# ADR-0009 — Adotar MVP executável Windows-native

**Status:** Accepted
**Date:** 2026-08-17
**Scope:** Portfolio MVP

## Context

A arquitetura-alvo original do projeto previa uma infraestrutura local mais
ampla, incluindo Docker Compose, Garage, PostgreSQL, Airflow, dbt, Superset e
uma stack dedicada de observabilidade.

Durante a implementação local, problemas no subsistema de virtualização/WSL
do Windows passaram a bloquear a execução da infraestrutura sem contribuir
diretamente para a validação das principais capacidades Data & AI do projeto.

O objetivo do MVP passou a ser entregar uma plataforma end-to-end executável,
auditável e reproduzível localmente, preservando a arquitetura-alvo como
possibilidade de evolução futura.

## Decision

O MVP executável adota:

- Python 3.12;
- filesystem local para dados de origem;
- Parquet como formato analítico materializado;
- DuckDB como warehouse analítico do MVP;
- schemas Bronze, Silver, Gold e Metrics;
- Streamlit para Business Intelligence;
- scikit-learn e XGBoost para Machine Learning;
- MLflow local com SQLite para experiment tracking;
- FastAPI para serving analítico e preditivo;
- agente analítico governado baseado em tools explícitas e read-only;
- pytest para testes automatizados;
- Ruff para lint e formatação.

## Arquitetura executável

```text
Olist CSV
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
   +-- Bronze
   +-- Silver
   +-- Gold
   +-- Metrics
          |
          +-- Streamlit BI
          +-- XGBoost / MLflow
          +-- FastAPI
          +-- Governed Analytics Agent
```

## Relationship with previous ADRs

Este ADR não apaga nem reescreve as decisões arquiteturais anteriores.

PostgreSQL, Garage, Docker Compose, Airflow, dbt, Superset,
Prometheus/Grafana/OpenTelemetry e demais componentes continuam representando
a arquitetura-alvo de evolução da plataforma, mas foram retirados do caminho
crítico do MVP executável.

ADR-0003 e ADR-0008 permanecem relevantes para a arquitetura-alvo, mas não
descrevem o runtime atual do MVP.

## Machine Learning

O MVP implementa previsão de risco de atraso de entrega.

A modelagem respeita point-in-time correctness e utiliza apenas informações
disponíveis antes do resultado de entrega.

A divisão final é temporal:

```text
70% treino
15% validação
15% teste
```

O threshold de classificação é escolhido na validação. O conjunto de teste
não participa dessa escolha.

Resultados finais:

```text
ROC AUC   : 0.7259
PR AUC    : 0.1679
Precision : 0.1470
Recall    : 0.5528
F1        : 0.2323
Threshold : 0.42
```

## Agent scope

O agente do MVP é deliberadamente governado e determinístico.

Ele:

- possui apenas ferramentas analíticas aprovadas;
- usa o banco em modo read-only;
- não aceita SQL arbitrário;
- mantém contexto limitado entre rankings;
- distingue GMV de quantidade de pedidos;
- não possui credenciais administrativas;
- não executa ações sensíveis.

O projeto não afirma que o agente atual utiliza um LLM generativo.

A camada de tools pode futuramente ser conectada a um LLM sem conceder acesso
irrestrito ao warehouse.

## Consequences

### Positive

- reduz a complexidade operacional local;
- elimina dependência de virtualização no MVP;
- mantém o fluxo Data → Analytics → ML → Serving → Agent executável;
- melhora a reprodutibilidade em Windows;
- preserva a arquitetura futura;
- evita alegar como implementados componentes que não fazem parte do runtime.

### Trade-offs

O MVP atual não executa:

- Garage;
- PostgreSQL;
- Docker Compose como runtime principal;
- Airflow;
- dbt como pipeline principal;
- Superset;
- Prometheus;
- Grafana;
- OpenTelemetry;
- LLM generativo conectado ao agente.

Esses componentes permanecem parte da arquitetura-alvo e não são apresentados
como funcionalidades implementadas do MVP.
