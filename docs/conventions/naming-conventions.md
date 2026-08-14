# Naming conventions

**Status:** Approved v1.0

- Identificadores: `lowercase_snake_case`.
- Markdown: `lowercase-kebab-case.md`.
- ADR: `NNNN-short-decision-name.md`.
- Buckets: `lowercase-kebab-case`.
- Env vars: `UPPER_SNAKE_CASE`.
- Timestamps produzidos pela plataforma: ISO 8601 UTC.
- IDs técnicos novos: UUID v4 quando não houver ID natural.
- IDs documentais de fonte: `SRC-*`, `SYN-*`, `PLT-*`.

dbt:
- `stg_<source>__<entity>`
- `int_<domain>__<purpose>`
- `dim_<entity>`
- `fct_<event>`
- `mart_<domain>__<purpose>`

Airflow:
- DAG: `<domain>_<action>`
- task: `verb_noun`

Agent tools:
- verb + object, por exemplo `get_metric`, `get_delay_prediction`.
