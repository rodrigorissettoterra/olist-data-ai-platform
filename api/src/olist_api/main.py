from __future__ import annotations

import json
from pathlib import Path

import duckdb
import joblib
from fastapi import FastAPI, HTTPException

ROOT = Path(__file__).resolve().parents[3]

DB_PATH = ROOT / "data" / "warehouse" / "olist.duckdb"
MODEL_PATH = ROOT / "models" / "delivery_delay_pipeline.joblib"
METRICS_PATH = ROOT / "artifacts" / "ml" / "delivery_delay_metrics.json"


app = FastAPI(
    title="Olist Data & AI Platform API",
    version="1.0.0",
    description=(
        "Analytics and predictive serving API for the Olist Data & AI Platform."
    ),
)


def connect():
    return duckdb.connect(str(DB_PATH), read_only=True)


def load_model():
    if not MODEL_PATH.exists():
        raise RuntimeError("Model artifact not found.")

    return joblib.load(MODEL_PATH)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "database": DB_PATH.exists(),
        "model": MODEL_PATH.exists(),
    }


@app.get("/api/v1/kpis")
def executive_kpis():
    con = connect()

    try:
        row = con.execute("SELECT * FROM metrics.executive_kpis").df().iloc[0]

        return {
            key: (value.item() if hasattr(value, "item") else value)
            for key, value in row.to_dict().items()
        }

    finally:
        con.close()


@app.get("/api/v1/model/metrics")
def model_metrics():
    if not METRICS_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Model metrics not found.",
        )

    return json.loads(METRICS_PATH.read_text(encoding="utf-8"))


@app.get("/api/v1/predict/{order_id}")
def predict_delay(order_id: str):
    con = connect()

    try:
        df = con.execute(
            """
            WITH item_features AS (
                SELECT
                    oi.order_id,

                    avg(oi.price) AS avg_item_price,
                    max(oi.price) AS max_item_price,

                    avg(p.product_weight_g)
                        AS avg_product_weight_g,

                    avg(
                        p.product_length_cm *
                        p.product_height_cm *
                        p.product_width_cm
                    ) AS avg_product_volume_cm3,

                    mode(p.product_category_name_en)
                        AS main_category,

                    mode(s.seller_state)
                        AS main_seller_state

                FROM silver.order_items oi

                LEFT JOIN silver.products p
                    ON oi.product_id = p.product_id

                LEFT JOIN silver.sellers s
                    ON oi.seller_id = s.seller_id

                WHERE oi.order_id = ?

                GROUP BY oi.order_id
            )

            SELECT
                o.item_count,
                o.product_count,
                o.seller_count,
                o.item_gmv,
                o.freight_value,
                o.payment_value,
                o.payment_count,
                o.max_installments,

                f.avg_item_price,
                f.max_item_price,
                f.avg_product_weight_g,
                f.avg_product_volume_cm3,

                CASE
                    WHEN o.item_gmv > 0
                    THEN o.freight_value / o.item_gmv
                    ELSE 0
                END AS freight_ratio,

                date_diff(
                    'day',
                    o.order_purchase_ts,
                    o.order_estimated_delivery_ts
                ) AS promised_delivery_days,

                CASE
                    WHEN o.customer_state = f.main_seller_state
                    THEN 1
                    ELSE 0
                END AS same_state,

                extract(month from o.order_purchase_ts)
                    AS purchase_month,

                extract(dow from o.order_purchase_ts)
                    AS purchase_day_of_week,

                extract(hour from o.order_purchase_ts)
                    AS purchase_hour,

                o.customer_state,
                f.main_category,
                f.main_seller_state

            FROM gold.fact_orders o

            LEFT JOIN item_features f
                ON o.order_id = f.order_id

            WHERE o.order_id = ?
            """,
            [order_id, order_id],
        ).df()

    finally:
        con.close()

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail="Order not found.",
        )

    bundle = load_model()

    model = bundle["model"]
    threshold = bundle["threshold"]
    features = bundle["features"]

    X = df[features]

    probability = float(model.predict_proba(X)[0, 1])

    prediction = probability >= threshold

    return {
        "order_id": order_id,
        "delay_probability": round(probability, 4),
        "threshold": round(float(threshold), 4),
        "delay_risk": bool(prediction),
        "risk_label": ("high" if prediction else "low"),
    }
