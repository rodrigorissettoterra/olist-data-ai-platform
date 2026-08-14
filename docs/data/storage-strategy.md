# Estratégia de armazenamento

**Status:** Approved v1.0

## Regra central

```text
Git/GitHub   → código, configuração e documentação
Garage       → arquivos, Data Lake e artefatos
PostgreSQL   → dados relacionais, warehouse, marts e metadata
Google Drive → arquivo externo, snapshots e backups; nunca runtime obrigatório
```

## Garage

Buckets:

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
- versionamento de fonte e execução.

### Bronze

- Parquet;
- normalização técnica;
- schema/tipos técnicos;
- sem regra final de negócio.

### Silver

- Parquet;
- limpo, reconciliado e semanticamente coerente;
- permanece prioritariamente no lake.

### Gold

Pode existir em Parquet quando orientado a arquivo e em PostgreSQL quando
destinado a consulta relacional/serving.

## PostgreSQL

Database principal:

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

Databases internos separados no futuro:

- `airflow`
- `superset`
- `mlflow`

## MLflow

- backend metadata: PostgreSQL;
- artifacts: `olist-ml` no Garage.

## Formatos

| Camada | Formato |
|---|---|
| Source | original |
| Raw | original |
| Bronze | Parquet |
| Silver | Parquet |
| Gold file-based | Parquet |
| Feature datasets | Parquet |
| ML artifacts | nativo da ferramenta |

Compressão inicial preferida: Snappy.

## Backup

Prioridade:

1. fontes originais;
2. Raw;
3. metadata crítica;
4. configurações não versionadas necessárias à recuperação;
5. artefatos relevantes.

Google Drive é apenas camada auxiliar de arquivo/backup.

## Segurança

Consumidores usam menor privilégio. Agent e BI não recebem credenciais
administrativas. Credenciais entram via variáveis de ambiente e nunca são
versionadas.

## Portabilidade

Consumidores devem depender do contrato S3-compatible e não de APIs específicas
do Garage quando houver alternativa padrão. Isso permite futura migração sem
transformar AWS em dependência atual.
