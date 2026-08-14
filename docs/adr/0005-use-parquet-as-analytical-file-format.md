# ADR-0005 — Use Parquet as analytical file format

**Status:** Accepted
**Date:** 2026-08-14

## Decision
Raw preserva o formato original. Bronze, Silver, Gold file-based e feature
datasets utilizam Parquet como formato padrão, inicialmente com Snappy.

## Consequences
Formato aberto, colunar, comprimido e eficiente para DuckDB/Python.
