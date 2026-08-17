from __future__ import annotations

from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "warehouse" / "olist.duckdb"
SILVER_DIR = ROOT / "data" / "silver"
GOLD_DIR = ROOT / "data" / "gold"
METRICS_DIR = ROOT / "data" / "metrics"


def sql_path(path: Path) -> str:
    return "'" + path.as_posix().replace("'", "''") + "'"


def export_table(con: duckdb.DuckDBPyConnection, table: str, path: Path) -> None:
    con.execute(
        f"""
        COPY {table}
        TO {sql_path(path)}
        (FORMAT PARQUET, COMPRESSION SNAPPY)
        """
    )


def main() -> None:
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(DB_PATH))

    con.execute("CREATE SCHEMA IF NOT EXISTS silver")
    con.execute("CREATE SCHEMA IF NOT EXISTS gold")
    con.execute("CREATE SCHEMA IF NOT EXISTS metrics")

    print("Construindo Silver...")

    con.execute(
        """
        CREATE OR REPLACE TABLE silver.customers AS
        SELECT
            CAST(customer_id AS VARCHAR) AS customer_id,
            CAST(customer_unique_id AS VARCHAR) AS customer_unique_id,
            customer_zip_code_prefix,
            trim(customer_city) AS customer_city,
            upper(trim(customer_state)) AS customer_state
        FROM bronze.customers
        """
    )

    con.execute(
        """
        CREATE OR REPLACE TABLE silver.orders AS
        SELECT
            CAST(order_id AS VARCHAR) AS order_id,
            CAST(customer_id AS VARCHAR) AS customer_id,
            lower(trim(order_status)) AS order_status,
            try_cast(order_purchase_timestamp AS TIMESTAMP) AS order_purchase_ts,
            try_cast(order_approved_at AS TIMESTAMP) AS order_approved_ts,
            try_cast(order_delivered_carrier_date AS TIMESTAMP)
                AS order_delivered_carrier_ts,
            try_cast(order_delivered_customer_date AS TIMESTAMP)
                AS order_delivered_customer_ts,
            try_cast(order_estimated_delivery_date AS TIMESTAMP)
                AS order_estimated_delivery_ts
        FROM bronze.orders
        """
    )

    con.execute(
        """
        CREATE OR REPLACE TABLE silver.order_items AS
        SELECT
            CAST(order_id AS VARCHAR) AS order_id,
            CAST(order_item_id AS INTEGER) AS order_item_id,
            CAST(product_id AS VARCHAR) AS product_id,
            CAST(seller_id AS VARCHAR) AS seller_id,
            try_cast(shipping_limit_date AS TIMESTAMP) AS shipping_limit_ts,
            try_cast(price AS DOUBLE) AS price,
            try_cast(freight_value AS DOUBLE) AS freight_value
        FROM bronze.order_items
        """
    )

    con.execute(
        """
        CREATE OR REPLACE TABLE silver.order_payments AS
        SELECT
            CAST(order_id AS VARCHAR) AS order_id,
            CAST(payment_sequential AS INTEGER) AS payment_sequential,
            lower(trim(payment_type)) AS payment_type,
            CAST(payment_installments AS INTEGER) AS payment_installments,
            try_cast(payment_value AS DOUBLE) AS payment_value
        FROM bronze.order_payments
        """
    )

    con.execute(
        """
        CREATE OR REPLACE TABLE silver.order_reviews AS
        SELECT
            CAST(review_id AS VARCHAR) AS review_id,
            CAST(order_id AS VARCHAR) AS order_id,
            CAST(review_score AS INTEGER) AS review_score,
            review_comment_title,
            review_comment_message,
            try_cast(review_creation_date AS TIMESTAMP) AS review_creation_ts,
            try_cast(review_answer_timestamp AS TIMESTAMP) AS review_answer_ts
        FROM bronze.order_reviews
        """
    )

    con.execute(
        """
        CREATE OR REPLACE TABLE silver.products AS
        SELECT
            CAST(p.product_id AS VARCHAR) AS product_id,
            p.product_category_name,
            COALESCE(
                t.product_category_name_english,
                p.product_category_name,
                'unknown'
            ) AS product_category_name_en,
            try_cast(p.product_name_lenght AS INTEGER) AS product_name_length,
            try_cast(p.product_description_lenght AS INTEGER)
                AS product_description_length,
            try_cast(p.product_photos_qty AS INTEGER) AS product_photos_qty,
            try_cast(p.product_weight_g AS DOUBLE) AS product_weight_g,
            try_cast(p.product_length_cm AS DOUBLE) AS product_length_cm,
            try_cast(p.product_height_cm AS DOUBLE) AS product_height_cm,
            try_cast(p.product_width_cm AS DOUBLE) AS product_width_cm
        FROM bronze.products p
        LEFT JOIN bronze.product_category_name_translation t
            ON p.product_category_name = t.product_category_name
        """
    )

    con.execute(
        """
        CREATE OR REPLACE TABLE silver.sellers AS
        SELECT
            CAST(seller_id AS VARCHAR) AS seller_id,
            seller_zip_code_prefix,
            trim(seller_city) AS seller_city,
            upper(trim(seller_state)) AS seller_state
        FROM bronze.sellers
        """
    )

    con.execute(
        """
        CREATE OR REPLACE TABLE silver.geolocation_zip AS
        SELECT
            geolocation_zip_code_prefix,
            trim(geolocation_city) AS geolocation_city,
            upper(trim(geolocation_state)) AS geolocation_state,
            avg(try_cast(geolocation_lat AS DOUBLE)) AS latitude,
            avg(try_cast(geolocation_lng AS DOUBLE)) AS longitude,
            count(*) AS source_rows
        FROM bronze.geolocation
        GROUP BY 1, 2, 3
        """
    )

    con.execute(
        """
        CREATE OR REPLACE TABLE silver.marketing_qualified_leads AS
        SELECT
            CAST(mql_id AS VARCHAR) AS mql_id,
            try_cast(first_contact_date AS DATE) AS first_contact_date,
            CAST(landing_page_id AS VARCHAR) AS landing_page_id,
            lower(trim(origin)) AS origin
        FROM bronze.marketing_qualified_leads
        """
    )

    con.execute(
        """
        CREATE OR REPLACE TABLE silver.closed_deals AS
        SELECT
            CAST(mql_id AS VARCHAR) AS mql_id,
            CAST(seller_id AS VARCHAR) AS seller_id,
            CAST(sdr_id AS VARCHAR) AS sdr_id,
            CAST(sr_id AS VARCHAR) AS sr_id,
            try_cast(won_date AS TIMESTAMP) AS won_ts,
            business_segment,
            lead_type,
            lead_behaviour_profile,
            has_company,
            has_gtin,
            average_stock,
            business_type,
            try_cast(declared_product_catalog_size AS INTEGER)
                AS declared_product_catalog_size,
            try_cast(declared_monthly_revenue AS DOUBLE)
                AS declared_monthly_revenue
        FROM bronze.closed_deals
        """
    )

    print("  Silver OK")

    print("Construindo Gold...")

    con.execute(
        """
        CREATE OR REPLACE TABLE gold.dim_customers AS
        SELECT DISTINCT
            customer_unique_id,
            customer_city,
            customer_state
        FROM silver.customers
        """
    )

    con.execute(
        """
        CREATE OR REPLACE TABLE gold.dim_products AS
        SELECT *
        FROM silver.products
        """
    )

    con.execute(
        """
        CREATE OR REPLACE TABLE gold.fact_orders AS
        WITH item_agg AS (
            SELECT
                order_id,
                count(*) AS item_count,
                count(DISTINCT product_id) AS product_count,
                count(DISTINCT seller_id) AS seller_count,
                sum(price) AS item_gmv,
                sum(freight_value) AS freight_value
            FROM silver.order_items
            GROUP BY order_id
        ),
        payment_agg AS (
            SELECT
                order_id,
                count(*) AS payment_count,
                sum(payment_value) AS payment_value,
                max(payment_installments) AS max_installments
            FROM silver.order_payments
            GROUP BY order_id
        ),
        review_agg AS (
            SELECT
                order_id,
                avg(review_score) AS review_score
            FROM silver.order_reviews
            GROUP BY order_id
        )
        SELECT
            o.order_id,
            o.customer_id,
            c.customer_unique_id,
            c.customer_city,
            c.customer_state,
            o.order_status,

            o.order_purchase_ts,
            o.order_approved_ts,
            o.order_delivered_carrier_ts,
            o.order_delivered_customer_ts,
            o.order_estimated_delivery_ts,

            COALESCE(i.item_count, 0) AS item_count,
            COALESCE(i.product_count, 0) AS product_count,
            COALESCE(i.seller_count, 0) AS seller_count,

            COALESCE(i.item_gmv, 0) AS item_gmv,
            COALESCE(i.freight_value, 0) AS freight_value,
            COALESCE(p.payment_value, 0) AS payment_value,
            COALESCE(p.payment_count, 0) AS payment_count,
            COALESCE(p.max_installments, 0) AS max_installments,

            r.review_score,

            CASE
                WHEN o.order_purchase_ts IS NOT NULL
                 AND o.order_delivered_customer_ts IS NOT NULL
                THEN date_diff(
                    'day',
                    o.order_purchase_ts,
                    o.order_delivered_customer_ts
                )
            END AS delivery_time_days,

            CASE
                WHEN o.order_estimated_delivery_ts IS NOT NULL
                 AND o.order_delivered_customer_ts IS NOT NULL
                THEN date_diff(
                    'day',
                    o.order_estimated_delivery_ts,
                    o.order_delivered_customer_ts
                )
            END AS delivery_delay_days,

            CASE
                WHEN o.order_estimated_delivery_ts IS NOT NULL
                 AND o.order_delivered_customer_ts IS NOT NULL
                THEN o.order_delivered_customer_ts
                     > o.order_estimated_delivery_ts
            END AS is_delayed

        FROM silver.orders o
        LEFT JOIN silver.customers c
            ON o.customer_id = c.customer_id
        LEFT JOIN item_agg i
            ON o.order_id = i.order_id
        LEFT JOIN payment_agg p
            ON o.order_id = p.order_id
        LEFT JOIN review_agg r
            ON o.order_id = r.order_id
        """
    )

    con.execute(
        """
        CREATE OR REPLACE TABLE gold.fact_order_items AS
        SELECT
            oi.order_id,
            oi.order_item_id,
            oi.product_id,
            oi.seller_id,
            p.product_category_name,
            p.product_category_name_en,
            oi.price,
            oi.freight_value,
            oi.shipping_limit_ts
        FROM silver.order_items oi
        LEFT JOIN silver.products p
            ON oi.product_id = p.product_id
        """
    )

    print("  Gold OK")

    print("Construindo Metrics Layer...")

    con.execute(
        """
        CREATE OR REPLACE TABLE metrics.executive_kpis AS
        SELECT
            count(*) AS total_orders,
            count(DISTINCT customer_unique_id) AS unique_customers,

            count(*) FILTER (
                WHERE order_status = 'delivered'
            ) AS delivered_orders,

            count(*) FILTER (
                WHERE order_status = 'canceled'
            ) AS canceled_orders,

            round(sum(item_gmv), 2) AS total_gmv,
            round(sum(payment_value), 2) AS total_payments,

            round(
                sum(item_gmv) / NULLIF(count(*), 0),
                2
            ) AS avg_order_gmv,

            round(avg(review_score), 2) AS avg_review_score,

            round(
                100.0 * count(*) FILTER (
                    WHERE is_delayed = true
                )
                /
                NULLIF(
                    count(*) FILTER (
                        WHERE is_delayed IS NOT NULL
                    ),
                    0
                ),
                2
            ) AS delayed_delivery_pct,

            round(
                avg(delivery_time_days) FILTER (
                    WHERE delivery_time_days IS NOT NULL
                ),
                2
            ) AS avg_delivery_days

        FROM gold.fact_orders
        """
    )

    con.execute(
        """
        CREATE OR REPLACE TABLE metrics.monthly_sales AS
        SELECT
            CAST(date_trunc('month', order_purchase_ts) AS DATE)
                AS purchase_month,

            count(*) AS orders,
            count(DISTINCT customer_unique_id) AS customers,

            round(sum(item_gmv), 2) AS gmv,
            round(sum(payment_value), 2) AS payments,

            round(
                sum(item_gmv) / NULLIF(count(*), 0),
                2
            ) AS avg_order_gmv,

            round(avg(review_score), 2) AS avg_review_score,

            round(
                100.0 * count(*) FILTER (
                    WHERE is_delayed = true
                )
                /
                NULLIF(
                    count(*) FILTER (
                        WHERE is_delayed IS NOT NULL
                    ),
                    0
                ),
                2
            ) AS delayed_delivery_pct

        FROM gold.fact_orders
        WHERE order_purchase_ts IS NOT NULL
        GROUP BY 1
        ORDER BY 1
        """
    )

    con.execute(
        """
        CREATE OR REPLACE TABLE metrics.category_performance AS
        SELECT
            COALESCE(product_category_name_en, 'unknown') AS category,
            count(*) AS items,
            count(DISTINCT order_id) AS orders,
            round(sum(price), 2) AS gmv,
            round(avg(price), 2) AS avg_item_price
        FROM gold.fact_order_items
        GROUP BY 1
        ORDER BY gmv DESC
        """
    )

    con.execute(
        """
        CREATE OR REPLACE TABLE metrics.state_performance AS
        SELECT
            customer_state AS state,
            count(*) AS orders,
            count(DISTINCT customer_unique_id) AS customers,
            round(sum(item_gmv), 2) AS gmv,
            round(avg(review_score), 2) AS avg_review_score,

            round(
                100.0 * count(*) FILTER (
                    WHERE is_delayed = true
                )
                /
                NULLIF(
                    count(*) FILTER (
                        WHERE is_delayed IS NOT NULL
                    ),
                    0
                ),
                2
            ) AS delayed_delivery_pct

        FROM gold.fact_orders
        WHERE customer_state IS NOT NULL
        GROUP BY 1
        ORDER BY gmv DESC
        """
    )

    print("  Metrics OK")

    silver_tables = [
        "customers",
        "orders",
        "order_items",
        "order_payments",
        "order_reviews",
        "products",
        "sellers",
        "geolocation_zip",
        "marketing_qualified_leads",
        "closed_deals",
    ]

    for table in silver_tables:
        export_table(
            con,
            f"silver.{table}",
            SILVER_DIR / f"{table}.parquet",
        )

    export_table(
        con,
        "gold.fact_orders",
        GOLD_DIR / "fact_orders.parquet",
    )
    export_table(
        con,
        "gold.fact_order_items",
        GOLD_DIR / "fact_order_items.parquet",
    )
    export_table(
        con,
        "gold.dim_customers",
        GOLD_DIR / "dim_customers.parquet",
    )
    export_table(
        con,
        "gold.dim_products",
        GOLD_DIR / "dim_products.parquet",
    )

    for table in [
        "executive_kpis",
        "monthly_sales",
        "category_performance",
        "state_performance",
    ]:
        export_table(
            con,
            f"metrics.{table}",
            METRICS_DIR / f"{table}.parquet",
        )

    fact_count = con.execute("SELECT count(*) FROM gold.fact_orders").fetchone()[0]

    con.close()

    print()
    print(f"Fact orders: {fact_count:,}")
    print("BUILD SILVER/GOLD/METRICS OK")


if __name__ == "__main__":
    main()
