# Catálogo das fontes

**Status:** MVP real sources implemented; synthetic sources deferred by ADR-0009

> **Implementation note:** this document was originally created for the broader
> production-oriented target architecture. The executable Windows-native MVP
> adopted in `docs/adr/0009-adopt-windows-native-mvp.md` uses only the two real
> public Olist sources described below. Synthetic datasets remain documented as
> a future evolution path and are not current runtime requirements.

## Classificação

- `REAL_EXTERNAL`
- `SYNTHETIC_DERIVED` — target architecture / deferred
- `PLATFORM_GENERATED`

## SRC-001 — Olist Brazilian E-Commerce Dataset

Arquivos:

1. `olist_customers_dataset.csv`
2. `olist_geolocation_dataset.csv`
3. `olist_order_items_dataset.csv`
4. `olist_order_payments_dataset.csv`
5. `olist_order_reviews_dataset.csv`
6. `olist_orders_dataset.csv`
7. `olist_products_dataset.csv`
8. `olist_sellers_dataset.csv`
9. `product_category_name_translation.csv`

### Customers

Campos:
`customer_id`, `customer_unique_id`, `customer_zip_code_prefix`,
`customer_city`, `customer_state`.

`customer_id` liga o registro ao pedido; `customer_unique_id` identifica o
cliente lógico anonimizado entre pedidos.

### Orders

Campos:
`order_id`, `customer_id`, `order_status`, `order_purchase_timestamp`,
`order_approved_at`, `order_delivered_carrier_date`,
`order_delivered_customer_date`, `order_estimated_delivery_date`.

`order_delivered_customer_date` é posterior ao resultado e não é utilizado como
feature de previsão do risco de atraso.

### Order Items

Grain esperado: `order_id + order_item_id`.

Campos:
`order_id`, `order_item_id`, `product_id`, `seller_id`,
`shipping_limit_date`, `price`, `freight_value`.

### Payments

Grain esperado: `order_id + payment_sequential`.

Campos:
`order_id`, `payment_sequential`, `payment_type`,
`payment_installments`, `payment_value`.

Um pedido pode ter múltiplos pagamentos.

### Reviews

Campos:
`review_id`, `order_id`, `review_score`, `review_comment_title`,
`review_comment_message`, `review_creation_date`,
`review_answer_timestamp`.

A modelagem não presume uma única review por `order_id` antes da consolidação.

### Products

Campos:
`product_id`, `product_category_name`, `product_name_lenght`,
`product_description_lenght`, `product_photos_qty`, `product_weight_g`,
`product_length_cm`, `product_height_cm`, `product_width_cm`.

Raw preserva inclusive as grafias originais `lenght`.

### Sellers

Campos:
`seller_id`, `seller_zip_code_prefix`, `seller_city`, `seller_state`.

`seller_id` é a ponte principal com o Marketing Funnel.

### Geolocation

Campos:
`geolocation_zip_code_prefix`, `geolocation_lat`, `geolocation_lng`,
`geolocation_city`, `geolocation_state`.

A fonte possui múltiplos registros por prefixo de CEP. O MVP consolida essa
informação na camada Silver em `silver.geolocation_zip`.

### Product Category Translation

Campos:
`product_category_name`, `product_category_name_english`.

## SRC-002 — Olist Marketing Funnel

Arquivos:

1. `olist_marketing_qualified_leads_dataset.csv`
2. `olist_closed_deals_dataset.csv`

### Marketing Qualified Leads

Campos:
`mql_id`, `first_contact_date`, `landing_page_id`, `origin`.

### Closed Deals

Campos:
`mql_id`, `seller_id`, `sdr_id`, `sr_id`, `won_date`,
`business_segment`, `lead_type`, `lead_behaviour_profile`, `has_company`,
`has_gtin`, `average_stock`, `business_type`,
`declared_product_catalog_size`, `declared_monthly_revenue`.

Ponte:

```text
closed_deals.seller_id → sellers.seller_id
```

O funil não é presumido como cobrindo todo o período do e-commerce.

## Aquisição no MVP

O helper opcional `scripts/data/download_olist.py` baixa as duas fontes públicas
e disponibiliza os 11 CSVs esperados em `data/raw/`.

O build Bronze registra em `meta.ingestion_manifest`:

- `source_file`;
- `table_name`;
- `row_count`;
- `size_bytes`;
- `sha256`;
- `ingested_at`.

A versão exata do dataset no catálogo externo não é persistida pelo MVP atual;
por isso a documentação não a apresenta como metadado implementado.

## Fontes sintéticas — target architecture / deferred

Os itens abaixo pertencem à arquitetura-alvo original e não fazem parte do
runtime do MVP executável.

### SYN-001 — Inventory Snapshots

Planejado para evolução futura. Grain conceitual candidato:
`snapshot_timestamp + seller_id + product_id`.

### SYN-002 — Operational Events

Planejado para evolução futura quando for necessário representar estados
operacionais ausentes das fontes reais.

### SYN-003 — Campaigns

Opcional na arquitetura-alvo.

### SYN-004 — Web Events

Opcional na arquitetura-alvo.

### Provenance de dados sintéticos futuros

Caso fontes sintéticas sejam implementadas futuramente, deverão registrar:

- synthetic source ID;
- generator version;
- seed;
- generated_at;
- input dataset versions;
- configuration version.

## Cardinalidades e contratos

Contratos relevantes da fonte incluem:

- `orders.order_id` unique;
- `customers.customer_id` unique;
- `products.product_id` unique;
- `sellers.seller_id` unique;
- `mql.mql_id` unique;
- `order_items`: `order_id + order_item_id`;
- `payments`: `order_id + payment_sequential`;
- relações entre orders/customers/items/products/sellers/payments/reviews;
- `closed_deals.mql_id → mql.mql_id`;
- `closed_deals.seller_id → sellers.seller_id`.

O MVP valida diretamente os contratos necessários ao fluxo executável por meio
das transformações determinísticas e da suíte de integração. Contratos mais
amplos de profiling permanecem possíveis extensões de Data Quality.

## Fan-out

KPIs monetários não são calculados diretamente sobre joins multi-grão sem
agregação explícita. Orders, items, payments e reviews podem multiplicar linhas
quando combinados.
