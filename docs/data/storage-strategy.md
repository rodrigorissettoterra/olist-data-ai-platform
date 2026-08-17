# Estratégia de armazenamento

**Status:** Target architecture reference; MVP runtime superseded by ADR-0009

> **Implementation note:** this document records the original production-oriented
> storage strategy. The executable MVP adopted in
> `docs/adr/0009-adopt-windows-native-mvp.md` does not use Garage or PostgreSQL
> as runtime dependencies. The current implementation uses local source files,
> Parquet, DuckDB and local MLflow/SQLite. The sections below are retained as the
> target architecture for future evolution.

## Armazenamento do MVP executável

```text
Git/GitHub      → código, configuração e documentação
local data/raw  → arquivos-fonte públicos
local Parquet   → camada Bronze materializada
duckdb file     → Bronze, Silver, Gold, Metrics e metadata de ingestão
local MLflow    → experiment tracking com SQLite
local artifacts → modelo e métricas geradas
```

Dados gerados, bancos locais, artefatos de ML e secrets permanecem fora do Git.

## Estratégia-alvo preservada

```text
Git/GitHub   → código, configuração e documentação
Garage       → arquivos, Data Lake e artefatos
PostgreSQL   → dados relacionais, warehouse, marts e metadata
Google Drive → arquivo externo, snapshots e backups; nunca runtime obrigatório
```

## Garage — target architecture

Buckets previstos:

- `olist-raw`
- `olist-bronze`
- `olist-silver`
- `olist-gold`
- `olist-ml`

### Raw

- formato original;
- imutável;
- preserva origem;
- SHA-256;
- versionamento de fonte e execução quando a arquitetura-alvo for adotada.

### Bronze

- Parquet;
- normalização técnica;
- schema/tipos técnicos;
- sem regra final de negócio.

### Silver

- Parquet;
- limpo, reconciliado e semanticamente coerente;
- prioritariamente no lake na arquitetura-alvo.

### Gold

Na arquitetura-alvo, pode existir em Parquet quando orientado a arquivo e em
PostgreSQL quando destinado a consulta relacional/serving.

## PostgreSQL — target architecture

Database principal previsto:

`olist_warehouse`

Schemas previstos:

- `platform`
- `raw_meta`
- `staging`
- `intermediate`
- `analytics`
- `metrics`
- `ml`
- `agent`
- `observability` quando justificável

Databases internos separados previstos para:

- `airflow`
- `superset`
- `mlflow`

## MLflow

### MVP atual

- backend/tracking local com SQLite;
- artefatos gerados localmente e ignorados pelo Git.

### Target architecture

- backend metadata: PostgreSQL;
- artifacts: `olist-ml` no Garage.

## Formatos

| Camada | MVP atual | Target architecture |
|---|---|---|
| Source | CSV local | original |
| Raw | CSV local | original / Garage |
| Bronze | Parquet + DuckDB | Parquet |
| Silver | DuckDB | Parquet / PostgreSQL |
| Gold | DuckDB | Parquet / PostgreSQL |
| Metrics | DuckDB | PostgreSQL / Metrics Layer |
| ML artifacts | local | Garage / formato nativo |

Compressão Bronze do MVP: Snappy.

## Backup

A estratégia de backup operacional completa pertence à evolução futura. Para o
MVP reproduzível, as fontes públicas podem ser readquiridas e os demais dados e
artefatos são reconstruídos pelos scripts documentados.

Na arquitetura-alvo, a prioridade permanece:

1. fontes originais;
2. Raw;
3. metadata crítica;
4. configurações não versionadas necessárias à recuperação;
5. artefatos relevantes.

Google Drive é apenas uma possível camada auxiliar de arquivo/backup e nunca é
dependência do runtime do projeto.

## Segurança

Consumidores usam menor privilégio. O Agent do MVP acessa DuckDB em modo
read-only e não recebe credenciais administrativas. Secrets nunca são
versionados.

## Portabilidade futura

A arquitetura-alvo preserva contrato S3-compatible para permitir futura
migração de object storage sem transformar um provedor de cloud específico em
dependência do MVP atual.
