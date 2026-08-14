# Definition of Done

**Status:** Approved v1.0

## Regra geral

> Done significa implementado, validado, reproduzível, documentado e coerente
> com a arquitetura.

Uma tarefa não está concluída apenas porque o código foi escrito ou um container
subiu.

## DoD de tarefa

Quando aplicável:

- escopo implementado sem requisito obrigatório omitido;
- código/configuração no diretório correto;
- secrets fora do Git;
- testes adequados passando;
- comportamento de erro testado;
- reexecução/idempotência validada quando contratada;
- documentação atualizada;
- sem dependência manual oculta quando provisioning é possível;
- menor privilégio e exposição mínima;
- logging apropriado;
- sem alteração silenciosa de arquitetura.

## Dados

- Raw permanece imutável.
- Provenance e checksum preservados.
- Grain documentado.
- Joins multi-grão avaliados contra fan-out.
- Dados sintéticos nunca são apresentados como observados.
- Métricas oficiais possuem definição, grain, filtros, unidade e testes.

## ML

Um modelo requer problem statement, target, prediction point, leakage analysis,
dataset versionado, split adequado, baseline, evaluation, error analysis, seed e
model card.

## Agent/HITL

Tool deve ter contrato, permissão e testes. Número quantitativo deve ser
rastreável a evidence. Ação sensível requer proposta → aprovação → execução →
auditoria. Prompt pedindo "cuidado" não substitui enforcement programático.

## Infra

Serviço containerizado exige versão pinada, config, volume quando stateful,
network, healthcheck e exposição mínima quando aplicável.

Bootstrap deve ser reexecutável, preservar secrets existentes, validar
pré-requisitos, não destruir estado implicitamente e retornar exit code != 0 em
falha.

## Gate específico M0

Todos devem ser satisfeitos:

1. Project Charter aprovado/materializado.
2. Arquitetura v1 aprovada/materializada.
3. Estrutura aprovada.
4. Storage Strategy aprovada.
5. Source Catalog aprovado.
6. Convenções aprovadas.
7. ADRs coerentes; ADR-0002 Superseded e ADR-0008 Accepted.
8. README reflete estado real.
9. `LICENSE`, `NOTICE` e licença documental presentes.
10. `.gitignore` protege `.env`, runtime, dados e artifacts.
11. `.env.example` sem secrets reais.
12. `.gitattributes` garante LF.
13. `docker compose config --quiet` passa.
14. PostgreSQL healthy.
15. Garage healthy.
16. volumes persistentes configurados.
17. rede aprovada.
18. portas publicadas apenas em loopback quando necessário.
19. bootstrap existe.
20. segunda execução do bootstrap preserva secrets/estado.
21. buckets `olist-raw`, `olist-bronze`, `olist-silver`, `olist-gold`,
    `olist-ml` existem.
22. pipeline não possui acesso antecipado a `olist-ml`.
23. `.env` não está tracked.
24. backlog aprovado.
25. DoD aprovado.
26. working tree sem mudanças não intencionais.
27. commits coerentes de Foundation.
28. nenhuma ingestão/transformação/BI/ML/Agent antecipados.

Somente após esse gate:

```text
M0 — DONE → M1 autorizado
```
