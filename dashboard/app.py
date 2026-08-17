from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "warehouse" / "olist.duckdb"
MODEL_METRICS_PATH = ROOT / "artifacts" / "ml" / "delivery_delay_metrics.json"


st.set_page_config(
    page_title="Olist Data & AI Platform",
    page_icon="📊",
    layout="wide",
)


@st.cache_data
def query(sql: str) -> pd.DataFrame:
    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        return con.execute(sql).df()
    finally:
        con.close()


def brl(value: float) -> str:
    return f"R$ {value:,.2f}"


def load_model_metrics() -> dict[str, float] | None:
    if not MODEL_METRICS_PATH.exists():
        return None
    return json.loads(MODEL_METRICS_PATH.read_text(encoding="utf-8"))


st.title("Olist Data & AI Platform")
st.caption(
    "End-to-end analytics platform built from the Brazilian Olist e-commerce dataset."
)

overview_tab, sales_tab, operations_tab, ai_tab = st.tabs(
    [
        "Executive Overview",
        "Sales & Customers",
        "Operations & Logistics",
        "Predictive & AI Insights",
    ]
)


with overview_tab:
    kpi = query("SELECT * FROM metrics.executive_kpis").iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "GMV",
        brl(kpi["total_gmv"]),
    )
    col2.metric(
        "Orders",
        f"{int(kpi['total_orders']):,}",
    )
    col3.metric(
        "Customers",
        f"{int(kpi['unique_customers']):,}",
    )
    col4.metric(
        "Average Review",
        f"{kpi['avg_review_score']:.2f} / 5",
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Average Order GMV",
        brl(kpi["avg_order_gmv"]),
    )
    col2.metric(
        "Delivered Orders",
        f"{int(kpi['delivered_orders']):,}",
    )
    col3.metric(
        "Delayed Deliveries",
        f"{kpi['delayed_delivery_pct']:.2f}%",
    )
    col4.metric(
        "Average Delivery",
        f"{kpi['avg_delivery_days']:.1f} days",
    )

    st.divider()

    monthly = query(
        """
        SELECT
            purchase_month,
            gmv,
            orders,
            customers
        FROM metrics.monthly_sales
        ORDER BY purchase_month
        """
    )

    st.subheader("GMV evolution")

    chart = monthly.set_index("purchase_month")[["gmv"]]
    st.line_chart(chart)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top categories")

        categories = query(
            """
            SELECT
                category,
                gmv
            FROM metrics.category_performance
            ORDER BY gmv DESC
            LIMIT 10
            """
        )

        st.bar_chart(categories.set_index("category"))

    with col2:
        st.subheader("Top states")

        states = query(
            """
            SELECT
                state,
                gmv
            FROM metrics.state_performance
            ORDER BY gmv DESC
            LIMIT 10
            """
        )

        st.bar_chart(states.set_index("state"))


with sales_tab:
    st.header("Sales & Customers")

    monthly = query(
        """
        SELECT *
        FROM metrics.monthly_sales
        ORDER BY purchase_month
        """
    )

    metric = st.radio(
        "Monthly metric",
        ["GMV", "Orders", "Customers"],
        horizontal=True,
    )

    metric_map = {
        "GMV": "gmv",
        "Orders": "orders",
        "Customers": "customers",
    }

    selected = metric_map[metric]

    st.line_chart(monthly.set_index("purchase_month")[[selected]])

    st.subheader("Category performance")

    categories = query(
        """
        SELECT *
        FROM metrics.category_performance
        ORDER BY gmv DESC
        """
    )

    st.dataframe(
        categories,
        width="stretch",
        hide_index=True,
    )

    st.subheader("State performance")

    states = query(
        """
        SELECT *
        FROM metrics.state_performance
        ORDER BY gmv DESC
        """
    )

    st.dataframe(
        states,
        width="stretch",
        hide_index=True,
    )


with operations_tab:
    st.header("Operations & Logistics")

    operations = query(
        """
        SELECT
            order_status,
            count(*) AS orders
        FROM gold.fact_orders
        GROUP BY order_status
        ORDER BY orders DESC
        """
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Order status")
        st.bar_chart(operations.set_index("order_status"))

    with col2:
        logistics = query(
            """
            SELECT
                round(avg(delivery_time_days), 2)
                    AS avg_delivery_days,

                round(
                    avg(delivery_delay_days)
                    FILTER (WHERE delivery_delay_days > 0),
                    2
                ) AS avg_delay_days,

                count(*)
                    FILTER (WHERE is_delayed = true)
                    AS delayed_orders,

                count(*)
                    FILTER (WHERE is_delayed IS NOT NULL)
                    AS evaluated_deliveries

            FROM gold.fact_orders
            """
        ).iloc[0]

        st.metric(
            "Average delivery time",
            f"{logistics['avg_delivery_days']:.2f} days",
        )

        st.metric(
            "Average delay when late",
            f"{logistics['avg_delay_days']:.2f} days",
        )

        st.metric(
            "Delayed orders",
            f"{int(logistics['delayed_orders']):,}",
        )

    st.subheader("Delay rate by state")

    delays = query(
        """
        SELECT
            state,
            orders,
            delayed_delivery_pct
        FROM metrics.state_performance
        WHERE orders >= 100
        ORDER BY delayed_delivery_pct DESC
        """
    )

    st.bar_chart(delays.set_index("state")[["delayed_delivery_pct"]])

    st.dataframe(
        delays,
        width="stretch",
        hide_index=True,
    )


with ai_tab:
    st.header("Predictive & AI Insights")

    readiness = query(
        """
        SELECT
            count(*) AS total_orders,

            count(*)
                FILTER (
                    WHERE is_delayed IS NOT NULL
                ) AS labeled_orders,

            count(*)
                FILTER (
                    WHERE is_delayed = true
                ) AS delayed_orders,

            round(
                100.0 *
                count(*) FILTER (
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
            ) AS delayed_rate

        FROM gold.fact_orders
        """
    ).iloc[0]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Orders available",
        f"{int(readiness['total_orders']):,}",
    )

    col2.metric(
        "Orders with delivery outcome",
        f"{int(readiness['labeled_orders']):,}",
    )

    col3.metric(
        "Delay rate",
        f"{readiness['delayed_rate']:.2f}%",
    )

    metrics = load_model_metrics()

    if metrics is None:
        st.warning(
            "Model metrics were not found. Run the delivery-delay training "
            "pipeline to populate predictive metrics."
        )
    else:
        st.subheader("Delivery-delay model")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("ROC AUC", f"{metrics['roc_auc']:.4f}")
        col2.metric("PR AUC", f"{metrics['pr_auc']:.4f}")
        col3.metric("Recall", f"{metrics['recall']:.4f}")
        col4.metric("Threshold", f"{metrics['threshold']:.2f}")

        st.success(
            "The delivery-delay model, MLflow tracking, FastAPI prediction "
            "serving and governed analytics agent are implemented in the MVP."
        )


st.divider()

st.caption(
    "Data source: Olist Brazilian E-Commerce Dataset and "
    "Olist Marketing Funnel Dataset."
)
