from __future__ import annotations

import hashlib
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
BRONZE_DIR = ROOT / "data" / "bronze"
WAREHOUSE_DIR = ROOT / "data" / "warehouse"
DB_PATH = WAREHOUSE_DIR / "olist.duckdb"

EXPECTED_FILES = {
    "olist_customers_dataset.csv": "customers",
    "olist_geolocation_dataset.csv": "geolocation",
    "olist_orders_dataset.csv": "orders",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_order_reviews_dataset.csv": "order_reviews",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "product_category_name_translation.csv": "product_category_name_translation",
    "olist_closed_deals_dataset.csv": "closed_deals",
    "olist_marketing_qualified_leads_dataset.csv": "marketing_qualified_leads",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sql_path(path: Path) -> str:
    return "'" + path.as_posix().replace("'", "''") + "'"


def main() -> None:
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)

    available = {path.name: path for path in RAW_DIR.rglob("*.csv")}

    missing = sorted(set(EXPECTED_FILES) - set(available))
    if missing:
        raise RuntimeError(f"Arquivos ausentes: {', '.join(missing)}")

    con = duckdb.connect(str(DB_PATH))

    con.execute("CREATE SCHEMA IF NOT EXISTS bronze")
    con.execute("CREATE SCHEMA IF NOT EXISTS meta")

    con.execute(
        """
        CREATE OR REPLACE TABLE meta.ingestion_manifest (
            source_file VARCHAR,
            table_name VARCHAR,
            row_count BIGINT,
            size_bytes BIGINT,
            sha256 VARCHAR,
            ingested_at TIMESTAMP
        )
        """
    )

    print("Construindo camada Bronze...")

    for filename, table_name in EXPECTED_FILES.items():
        csv_path = available[filename]
        parquet_path = BRONZE_DIR / f"{table_name}.parquet"

        con.execute(
            f"""
            COPY (
                SELECT *
                FROM read_csv_auto(
                    {sql_path(csv_path)},
                    header = true,
                    sample_size = -1
                )
            )
            TO {sql_path(parquet_path)}
            (
                FORMAT PARQUET,
                COMPRESSION SNAPPY
            )
            """
        )

        con.execute(
            f"""
            CREATE OR REPLACE TABLE bronze."{table_name}" AS
            SELECT *
            FROM read_parquet({sql_path(parquet_path)})
            """
        )

        row_count = con.execute(
            f'SELECT COUNT(*) FROM bronze."{table_name}"'
        ).fetchone()[0]

        con.execute(
            """
            INSERT INTO meta.ingestion_manifest
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            [
                filename,
                table_name,
                row_count,
                csv_path.stat().st_size,
                sha256_file(csv_path),
            ],
        )

        print(f"  OK  {table_name:<36} {row_count:>10,} linhas")

    con.close()

    print()
    print(f"Bronze: {BRONZE_DIR}")
    print(f"DuckDB: {DB_PATH}")
    print("BUILD BRONZE OK")


if __name__ == "__main__":
    main()
