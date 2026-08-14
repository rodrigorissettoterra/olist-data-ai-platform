# ADR-0001 — Adopt local-first architecture

**Status:** Accepted
**Date:** 2026-08-14

## Context
O projeto deve executar sem cloud paga, trial ou serviço proprietário essencial.

## Decision
O núcleo será local-first e executado principalmente via Docker Compose.
Cloud pode existir apenas como extensão opcional.

## Consequences
Positivas: reprodutibilidade, baixo custo obrigatório, independência de
fornecedor. Trade-offs: mais provisioning e operação local.

## Alternatives Considered
Cloud-first e híbrido obrigatório foram rejeitados.
