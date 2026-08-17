from __future__ import annotations

import json
from pathlib import Path

import duckdb
import joblib
import mlflow
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "data" / "warehouse" / "olist.duckdb"
MODEL_DIR = ROOT / "models"
REPORT_DIR = ROOT / "artifacts" / "ml"
MLFLOW_DIR = ROOT / "data" / "mlflow"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)
MLFLOW_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> pd.DataFrame:
    con = duckdb.connect(str(DB), read_only=True)

    df = con.execute("""
        WITH item_features AS (
            SELECT
                oi.order_id,

                avg(oi.price) AS avg_item_price,
                max(oi.price) AS max_item_price,

                avg(p.product_weight_g) AS avg_product_weight_g,

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

            GROUP BY oi.order_id
        )

        SELECT
            o.order_purchase_ts,

            o.item_count,
            o.product_count,
            o.seller_count,

            o.item_gmv,
            o.freight_value,
            o.payment_value,
            o.payment_count,
            o.max_installments,

            o.customer_state,

            f.main_category,
            f.main_seller_state,
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

            cast(o.is_delayed AS INTEGER)
                AS target

        FROM gold.fact_orders o

        LEFT JOIN item_features f
            ON o.order_id = f.order_id

        WHERE
            o.order_status = 'delivered'
            AND o.is_delayed IS NOT NULL
            AND o.order_purchase_ts IS NOT NULL
            AND o.order_estimated_delivery_ts IS NOT NULL

        ORDER BY o.order_purchase_ts
    """).df()

    con.close()
    return df


def choose_threshold(y_true, probabilities):
    best_threshold = 0.50
    best_f1 = 0.0

    for threshold in np.arange(0.05, 0.81, 0.01):
        prediction = (probabilities >= threshold).astype(int)

        score = f1_score(
            y_true,
            prediction,
            zero_division=0,
        )

        if score > best_f1:
            best_f1 = score
            best_threshold = float(threshold)

    return best_threshold


def main():
    df = load_data()

    train_end = int(len(df) * 0.70)
    validation_end = int(len(df) * 0.85)

    train = df.iloc[:train_end]
    validation = df.iloc[train_end:validation_end]
    test = df.iloc[validation_end:]

    features = [
        "item_count",
        "product_count",
        "seller_count",
        "item_gmv",
        "freight_value",
        "payment_value",
        "payment_count",
        "max_installments",
        "avg_item_price",
        "max_item_price",
        "avg_product_weight_g",
        "avg_product_volume_cm3",
        "freight_ratio",
        "promised_delivery_days",
        "same_state",
        "purchase_month",
        "purchase_day_of_week",
        "purchase_hour",
        "customer_state",
        "main_category",
        "main_seller_state",
    ]

    categorical = [
        "customer_state",
        "main_category",
        "main_seller_state",
    ]

    numeric = [column for column in features if column not in categorical]

    preprocessing = ColumnTransformer(
        [
            (
                "numeric",
                SimpleImputer(strategy="median"),
                numeric,
            ),
            (
                "categorical",
                Pipeline(
                    [
                        (
                            "imputer",
                            SimpleImputer(strategy="most_frequent"),
                        ),
                        (
                            "encoder",
                            OneHotEncoder(handle_unknown="ignore"),
                        ),
                    ]
                ),
                categorical,
            ),
        ]
    )

    y_train = train["target"]

    positives = int(y_train.sum())
    negatives = len(y_train) - positives

    model = XGBClassifier(
        n_estimators=400,
        max_depth=6,
        learning_rate=0.04,
        subsample=0.85,
        colsample_bytree=0.85,
        scale_pos_weight=negatives / positives,
        min_child_weight=5,
        reg_lambda=2.0,
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1,
    )

    pipeline = Pipeline(
        [
            ("preprocessing", preprocessing),
            ("model", model),
        ]
    )

    print(f"Dataset:    {len(df):,}")
    print(f"Train:      {len(train):,}")
    print(f"Validation: {len(validation):,}")
    print(f"Test:       {len(test):,}")
    print()

    print(f"Delay rate train: {train['target'].mean():.4f}")
    print(f"Delay rate val:   {validation['target'].mean():.4f}")
    print(f"Delay rate test:  {test['target'].mean():.4f}")

    print()
    print("Treinando modelo final...")

    pipeline.fit(
        train[features],
        train["target"],
    )

    validation_prob = pipeline.predict_proba(validation[features])[:, 1]

    threshold = choose_threshold(
        validation["target"],
        validation_prob,
    )

    test_prob = pipeline.predict_proba(test[features])[:, 1]

    test_pred = (test_prob >= threshold).astype(int)

    metrics = {
        "roc_auc": float(
            roc_auc_score(
                test["target"],
                test_prob,
            )
        ),
        "pr_auc": float(
            average_precision_score(
                test["target"],
                test_prob,
            )
        ),
        "precision": float(
            precision_score(
                test["target"],
                test_pred,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                test["target"],
                test_pred,
                zero_division=0,
            )
        ),
        "f1": float(
            f1_score(
                test["target"],
                test_pred,
                zero_division=0,
            )
        ),
        "threshold": threshold,
        "test_delay_rate": float(test["target"].mean()),
    }

    joblib.dump(
        {
            "model": pipeline,
            "features": features,
            "threshold": threshold,
        },
        MODEL_DIR / "delivery_delay_pipeline.joblib",
    )

    metrics_path = REPORT_DIR / "delivery_delay_metrics.json"

    metrics_path.write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8",
    )

    mlflow.set_tracking_uri(
        "sqlite:///" + (MLFLOW_DIR / "mlflow.db").resolve().as_posix()
    )

    mlflow.set_experiment("olist-delivery-delay")

    with mlflow.start_run(run_name="xgboost-final-temporal"):
        mlflow.log_param(
            "split",
            "temporal_70_15_15",
        )

        mlflow.log_param(
            "feature_count",
            len(features),
        )

        for key, value in metrics.items():
            mlflow.log_metric(key, value)

        mlflow.log_artifact(str(metrics_path))

    print()
    print("FINAL TEST METRICS")
    print(f"ROC AUC   : {metrics['roc_auc']:.4f}")
    print(f"PR AUC    : {metrics['pr_auc']:.4f}")
    print(f"Precision : {metrics['precision']:.4f}")
    print(f"Recall    : {metrics['recall']:.4f}")
    print(f"F1        : {metrics['f1']:.4f}")
    print(f"Threshold : {metrics['threshold']:.2f}")

    print()
    print("FINAL TRAINING OK")


if __name__ == "__main__":
    main()
