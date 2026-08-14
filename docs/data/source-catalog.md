# Catálogo das fontes

**Status:** Approved v1.0

## Classificação

- `REAL_EXTERNAL`
- `SYNTHETIC_DERIVED`
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

`order_delivered_customer_date` é posterior ao resultado e não pode ser
automaticamente utilizado como feature de previsão.

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

Não presumir unicidade de `order_id`; a cardinalidade será medida.

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

Não presumir uma linha por prefixo de CEP; agregação/consolidação será definida
após profiling.

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

O funil não deve ser presumido como cobrindo todo o período do e-commerce.

## Fontes sintéticas

### SYN-001 — Inventory Snapshots

Obrigatória. Grain conceitual candidato:
`snapshot_timestamp + seller_id + product_id`.

Atributos somente serão congelados antes da implementação.

### SYN-002 — Operational Events

Obrigatória quando necessária para representar estados operacionais ausentes da
fonte real.

### SYN-003 — Campaigns

Opcional.

### SYN-004 — Web Events

Opcional.

## Regra de provenance sintético

Todo dataset sintético deve registrar:

- synthetic source ID;
- generator version;
- seed;
- generated_at;
- input dataset versions;
- configuration version.

## Cardinalidades a validar

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

Esses itens são contratos esperados a testar, não resultados já medidos.

## Fan-out

Nunca calcular KPI monetário em join multi-grão sem contrato explícito. Orders,
items, payments e reviews podem multiplicar linhas quando combinados.

## Versão de fontes

Cada arquivo adquirido deve registrar:

`source_id`, `source_version`, `file_name`, `SHA-256`, `file_size`,
`acquired_at`.
