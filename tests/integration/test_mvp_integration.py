from __future__ import annotations

import json
import sys
from pathlib import Path

import duckdb
import joblib
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(ROOT / "agent" / "src"))
sys.path.insert(0, str(ROOT / "api" / "src"))

from olist_agent.main import run_agent
from olist_api.main import app

DB_PATH = ROOT / "data" / "warehouse" / "olist.duckdb"
MODEL_PATH = ROOT / "models" / "delivery_delay_pipeline.joblib"
METRICS_PATH = ROOT / "artifacts" / "ml" / "delivery_delay_metrics.json"

client = TestClient(app)


def test_database_exists():
    assert DB_PATH.exists()


def test_expected_layers_exist():
    con = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        schemas = {
            row[0]
            for row in con.execute(
                """
                select schema_name
                from information_schema.schemata
                """
            ).fetchall()
        }

        assert "bronze" in schemas
        assert "silver" in schemas
        assert "gold" in schemas
        assert "metrics" in schemas

    finally:
        con.close()


def test_fact_orders_unique():
    con = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        total, unique_orders = con.execute(
            """
            select
                count(*) as total,
                count(distinct order_id) as unique_orders
            from gold.fact_orders
            """
        ).fetchone()

        assert total > 0
        assert total == unique_orders

    finally:
        con.close()


def test_executive_metrics_consistency():
    con = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        fact_orders = con.execute(
            """
            select count(*)
            from gold.fact_orders
            """
        ).fetchone()[0]

        row = con.execute(
            """
            select
                total_orders,
                total_gmv,
                delayed_delivery_pct,
                avg_review_score
            from metrics.executive_kpis
            """
        ).fetchone()

        assert row is not None
        assert int(row[0]) == fact_orders
        assert row[1] > 0
        assert 0 <= row[2] <= 100
        assert 0 <= row[3] <= 5

    finally:
        con.close()


def test_model_artifacts():
    assert MODEL_PATH.exists()
    assert METRICS_PATH.exists()

    bundle = joblib.load(MODEL_PATH)

    assert "model" in bundle
    assert "features" in bundle
    assert "threshold" in bundle

    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert metrics["roc_auc"] > 0.5
    assert 0 <= metrics["threshold"] <= 1


def test_agent_category_context():
    response = run_agent("Quais categorias têm maior número de pedidos?")

    assert response.tool == "categories_by_orders_high"

    response = run_agent(
        "E os menores?",
        last_tool=response.tool,
    )

    assert response.tool == "categories_by_orders_low"


def test_agent_gmv_context():
    response = run_agent("Quais categorias têm menor GMV?")

    assert response.tool == "categories_by_gmv_low"

    response = run_agent(
        "E as maiores?",
        last_tool=response.tool,
    )

    assert response.tool == "categories_by_gmv_high"


def test_agent_delay_context():
    response = run_agent("Quais estados têm maior taxa de atraso?")

    assert response.tool == "delay_by_state_high"

    response = run_agent(
        "E os menores?",
        last_tool=response.tool,
    )

    assert response.tool == "delay_by_state_low"


def test_api_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["database"] is True
    assert data["model"] is True


def test_api_kpis():
    response = client.get("/api/v1/kpis")

    assert response.status_code == 200

    data = response.json()

    assert data["total_orders"] > 0
    assert data["total_gmv"] > 0


def test_api_model_metrics():
    response = client.get("/api/v1/model/metrics")

    assert response.status_code == 200

    data = response.json()

    assert data["roc_auc"] > 0.5
    assert 0 <= data["threshold"] <= 1


def test_api_prediction():
    con = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        order_id = con.execute(
            """
            select order_id
            from gold.fact_orders
            where order_status = 'delivered'
              and is_delayed is not null
            limit 1
            """
        ).fetchone()[0]

    finally:
        con.close()

    response = client.get(f"/api/v1/predict/{order_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["order_id"] == order_id
    assert 0 <= data["delay_probability"] <= 1
    assert data["risk_label"] in {"low", "high"}
