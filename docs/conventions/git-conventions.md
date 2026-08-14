# Convenções Git

**Status:** Approved v1.0

Branch estável: `main`.

Branches curtas:
- `feat/`
- `fix/`
- `docs/`
- `refactor/`
- `test/`
- `chore/`

Commits: Conventional Commits.

Exemplos:
- `feat(airflow): add source ingestion DAG`
- `fix(dbt): prevent payment fan-out`
- `docs: add storage strategy`

Commits devem ser atômicos. Não usar Git LFS para datasets por padrão. Secrets,
datasets e outputs pesados não entram no Git.

Mudança arquitetural relevante exige change control/ADR antes da implementação.
