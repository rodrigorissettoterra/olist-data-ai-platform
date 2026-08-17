from __future__ import annotations

import shutil
from pathlib import Path

import kagglehub

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"

DATASETS = (
    "olistbr/brazilian-ecommerce",
    "olistbr/marketing-funnel-olist",
)

EXPECTED_FILES = {
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
    "olist_closed_deals_dataset.csv",
    "olist_marketing_qualified_leads_dataset.csv",
}


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    copied: set[str] = set()

    for dataset in DATASETS:
        print(f"Downloading {dataset}...")
        dataset_dir = Path(kagglehub.dataset_download(dataset))

        for source in dataset_dir.rglob("*.csv"):
            if source.name not in EXPECTED_FILES:
                continue

            destination = RAW_DIR / source.name
            shutil.copy2(source, destination)
            copied.add(source.name)
            print(f"  OK  {source.name}")

    available = {path.name for path in RAW_DIR.glob("*.csv")}
    missing = sorted(EXPECTED_FILES - available)

    if missing:
        raise RuntimeError(
            "Expected Olist files are still missing: " + ", ".join(missing)
        )

    print()
    print(f"Raw directory: {RAW_DIR}")
    print(f"Expected files available: {len(EXPECTED_FILES)}")
    print("OLIST DATA DOWNLOAD OK")


if __name__ == "__main__":
    main()
