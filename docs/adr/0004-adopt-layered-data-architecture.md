# ADR-0004 — Adopt layered data architecture

**Status:** Accepted
**Date:** 2026-08-14

## Decision
Adotar `Raw → Bronze → Silver → Gold`.

Raw preserva a fonte; Bronze normaliza tecnicamente; Silver reconcilia
semanticamente; Gold entrega produtos de consumo.

## Consequences
Melhor lineage e reconstrução, com custo de mais artefatos e disciplina de
fronteiras.
