# ADR-0002 — Use MinIO as object storage

**Status:** Superseded
**Date:** 2026-08-14
**Superseded by:** ADR-0008

## Context
MinIO foi inicialmente escolhido como object storage S3-compatible local.

## Decision
A decisão original era usar MinIO para Raw/Bronze/Silver/Gold file-based e ML.

## Consequences
A decisão deixou de ser adequada após reavaliação de manutenção/licenciamento
e foi substituída por Garage. Este ADR é preservado para manter o histórico.
