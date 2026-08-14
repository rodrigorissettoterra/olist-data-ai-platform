# ADR-0003 — Use PostgreSQL as analytical warehouse

**Status:** Accepted
**Date:** 2026-08-14

## Context
É necessário um serving store relacional local para facts, dimensions, marts,
Metrics Layer e metadata.

## Decision
PostgreSQL será warehouse relacional. Garage permanece responsável pelo lake.
DuckDB não será warehouse central.

## Consequences
Boa compatibilidade com dbt/Superset/FastAPI, com trade-off de não representar
um warehouse distribuído de escala massiva.
