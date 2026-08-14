# ADR-0008 — Adopt Garage as S3-compatible object storage

**Status:** Accepted
**Date:** 2026-08-14
**Supersedes:** ADR-0002

## Context
A estratégia original usava MinIO. Após reavaliação, a plataforma precisava
preservar OSS mantido, execução local independente e contrato S3-compatible.

## Decision
Garage é a implementação do object storage local.

Buckets:
- `olist-raw`
- `olist-bronze`
- `olist-silver`
- `olist-gold`
- `olist-ml`

Consumidores devem depender do contrato S3-compatible. Variáveis `S3_*` são
preferidas nos consumidores; `GARAGE_*` ficam restritas ao servidor/provisioning.

A Foundation usa Garage single-node com `replication_factor = 1`, explicitamente
como topologia de desenvolvimento, não alta disponibilidade.

## Consequences
Preserva local-first e portabilidade. Exige validar compatibilidade das operações
S3 realmente utilizadas e administrar o serviço local.

## Alternatives Considered
Legacy MinIO OSS, MinIO AIStor, SeaweedFS, filesystem local e cloud object
storage foram analisados. AWS não é dependência do projeto.
