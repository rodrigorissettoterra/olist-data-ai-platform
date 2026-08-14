# Convenções SQL e dbt

**Status:** Approved v1.0

- SQL em lowercase.
- Um campo por linha em consultas relevantes.
- joins com chave explícita.
- evitar `natural join`.
- evitar `select *` em modelos permanentes.
- grain documentado para todo modelo relevante.
- aliases devem preservar legibilidade.
- valores monetários precisam de significado/unidade explícitos.

dbt:
- sources declaradas;
- referências via `source()`/`ref()`;
- staging faz normalização leve;
- intermediate concentra transformações reutilizáveis;
- Gold recebe facts, dimensions e marts;
- testes: not_null, unique, relationships, accepted_values e customizados quando
  necessário.
