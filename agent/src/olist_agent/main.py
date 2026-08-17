from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[3]
DB_PATH = ROOT / "data" / "warehouse" / "olist.duckdb"


@dataclass
class AgentResponse:
    tool: str
    answer: str


def normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    return "".join(
        char for char in normalized if not unicodedata.combining(char)
    ).strip()


def query_one(sql: str, params=None):
    con = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        return con.execute(
            sql,
            params or [],
        ).fetchone()
    finally:
        con.close()


def query_all(sql: str, params=None):
    con = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        return con.execute(
            sql,
            params or [],
        ).fetchall()
    finally:
        con.close()


def brl(value: float) -> str:
    text = f"{value:,.2f}"
    text = text.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {text}"


def integer(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def wants_lowest(text: str) -> bool:
    return any(
        term in text
        for term in [
            "menor",
            "menores",
            "menos",
            "baixo",
            "baixa",
            "baixos",
            "baixas",
        ]
    )


def wants_highest(text: str) -> bool:
    return any(
        term in text
        for term in [
            "maior",
            "maiores",
            "mais",
            "alto",
            "alta",
            "altos",
            "altas",
        ]
    )


def data_sources() -> AgentResponse:
    return AgentResponse(
        tool="data_sources",
        answer=(
            "A plataforma utiliza dois datasets públicos da Olist: "
            "Olist Brazilian E-Commerce Dataset, com dados de pedidos, "
            "clientes, produtos, vendedores, pagamentos, avaliações e "
            "geolocalização; e Olist Marketing Funnel Dataset, com leads "
            "qualificados e negócios fechados. Ao todo, foram ingeridos "
            "11 arquivos CSV."
        ),
    )


def executive_summary() -> AgentResponse:
    row = query_one(
        """
        SELECT
            total_orders,
            unique_customers,
            total_gmv,
            avg_review_score,
            delayed_delivery_pct,
            avg_delivery_days
        FROM metrics.executive_kpis
        """
    )

    return AgentResponse(
        tool="executive_kpis",
        answer=(
            f"A plataforma registra {integer(row[0])} pedidos, "
            f"{integer(row[1])} clientes únicos e GMV de "
            f"{brl(row[2])}. A avaliação média é {row[3]:.2f}/5, "
            f"{row[4]:.2f}% das entregas avaliadas atrasaram e "
            f"o prazo médio de entrega foi {row[5]:.1f} dias."
        ),
    )


def categories_by_gmv(
    highest: bool = True,
    limit: int = 5,
) -> AgentResponse:
    direction = "DESC" if highest else "ASC"

    rows = query_all(
        f"""
        SELECT
            p.product_category_name_en AS category,
            count(DISTINCT oi.order_id) AS orders,
            sum(oi.price) AS gmv
        FROM silver.order_items oi

        LEFT JOIN silver.products p
            ON oi.product_id = p.product_id

        WHERE p.product_category_name_en IS NOT NULL

        GROUP BY p.product_category_name_en

        ORDER BY gmv {direction}

        LIMIT ?
        """,
        [limit],
    )

    items = [
        (f"{index}. {category}: {brl(gmv)} ({integer(orders)} pedidos)")
        for index, (category, orders, gmv) in enumerate(rows, start=1)
    ]

    ranking = "maior" if highest else "menor"

    return AgentResponse(
        tool=("categories_by_gmv_high" if highest else "categories_by_gmv_low"),
        answer=(
            f"Categorias com {ranking} GMV "
            "(soma do valor dos itens vendidos; "
            "não representa a receita da Olist):\n" + "\n".join(items)
        ),
    )


def categories_by_orders(
    highest: bool = True,
    limit: int = 5,
) -> AgentResponse:
    direction = "DESC" if highest else "ASC"

    rows = query_all(
        f"""
        SELECT
            p.product_category_name_en AS category,
            count(DISTINCT oi.order_id) AS orders,
            sum(oi.price) AS gmv
        FROM silver.order_items oi

        LEFT JOIN silver.products p
            ON oi.product_id = p.product_id

        WHERE p.product_category_name_en IS NOT NULL

        GROUP BY p.product_category_name_en

        ORDER BY orders {direction}, gmv DESC

        LIMIT ?
        """,
        [limit],
    )

    items = [
        (f"{index}. {category}: {integer(orders)} pedidos ({brl(gmv)} em GMV)")
        for index, (category, orders, gmv) in enumerate(rows, start=1)
    ]

    ranking = "maior" if highest else "menor"

    return AgentResponse(
        tool=("categories_by_orders_high" if highest else "categories_by_orders_low"),
        answer=(f"Categorias com {ranking} número de pedidos:\n" + "\n".join(items)),
    )


def states_by_gmv(limit: int = 5) -> AgentResponse:
    rows = query_all(
        """
        SELECT
            state,
            gmv,
            delayed_delivery_pct
        FROM metrics.state_performance
        ORDER BY gmv DESC
        LIMIT ?
        """,
        [limit],
    )

    items = [
        (f"{index}. {state}: {brl(gmv)} em GMV — atraso {delay:.2f}%")
        for index, (state, gmv, delay) in enumerate(rows, start=1)
    ]

    return AgentResponse(
        tool="states_by_gmv",
        answer=("Estados com maior GMV:\n" + "\n".join(items)),
    )


def delay_states(
    highest: bool = True,
    limit: int = 5,
) -> AgentResponse:
    direction = "DESC" if highest else "ASC"

    rows = query_all(
        f"""
        SELECT
            state,
            orders,
            delayed_delivery_pct
        FROM metrics.state_performance
        WHERE orders >= 100
          AND delayed_delivery_pct IS NOT NULL
        ORDER BY delayed_delivery_pct {direction}
        LIMIT ?
        """,
        [limit],
    )

    items = [
        (f"{index}. {state}: {delay:.2f}% ({integer(orders)} pedidos)")
        for index, (state, orders, delay) in enumerate(rows, start=1)
    ]

    ranking = "Maiores" if highest else "Menores"

    return AgentResponse(
        tool=("delay_by_state_high" if highest else "delay_by_state_low"),
        answer=(f"{ranking} taxas de atraso:\n" + "\n".join(items)),
    )


def order_lookup(order_id: str) -> AgentResponse:
    row = query_one(
        """
        SELECT
            order_id,
            is_delayed,
            delivery_delay_days,
            order_status
        FROM gold.fact_orders
        WHERE order_id = ?
        """,
        [order_id],
    )

    if row is None:
        return AgentResponse(
            tool="order_lookup",
            answer=f"Pedido {order_id} não encontrado.",
        )

    actual = (
        "atrasou"
        if row[1] is True
        else "não atrasou"
        if row[1] is False
        else "não possui resultado de entrega"
    )

    return AgentResponse(
        tool="order_lookup",
        answer=(
            f"Pedido {row[0]}: status {row[3]}; "
            f"historicamente {actual}. "
            f"Dias relativos ao prazo estimado: {row[2]}."
        ),
    )


def run_agent(
    question: str,
    last_tool: str | None = None,
) -> AgentResponse:
    text = normalize(question)

    order_match = re.search(
        r"\b[a-f0-9]{32}\b",
        text,
    )

    if order_match:
        return order_lookup(order_match.group(0))

    # -------------------------------------------------
    # Intenções explícitas sempre vencem o contexto.
    # -------------------------------------------------

    if any(
        term in text
        for term in [
            "base de dados",
            "bases de dados",
            "dataset",
            "datasets",
            "fonte dos dados",
            "fontes dos dados",
            "dados utilizados",
        ]
    ):
        return data_sources()

    if any(
        term in text
        for term in [
            "categoria",
            "categorias",
        ]
    ):
        highest = not wants_lowest(text)

        if any(
            term in text
            for term in [
                "pedido",
                "pedidos",
                "quantidade",
                "numero",
            ]
        ):
            return categories_by_orders(highest=highest)

        return categories_by_gmv(highest=highest)

    if "atras" in text:
        highest = not wants_lowest(text)

        if any(
            term in text
            for term in [
                "estado",
                "estados",
                "uf",
            ]
        ):
            return delay_states(highest=highest)

    if any(
        term in text
        for term in [
            "estado",
            "estados",
            "regiao",
        ]
    ):
        return states_by_gmv()

    if any(
        term in text
        for term in [
            "resumo",
            "kpi",
            "indicador",
            "visao geral",
            "clientes",
        ]
    ):
        return executive_summary()

    # -------------------------------------------------
    # Continuação contextual.
    # Só entra aqui quando a pergunta não definiu
    # explicitamente um novo assunto.
    # -------------------------------------------------

    if last_tool in {
        "categories_by_orders_high",
        "categories_by_orders_low",
    }:
        if wants_lowest(text):
            return categories_by_orders(highest=False)

        if wants_highest(text):
            return categories_by_orders(highest=True)

    if last_tool in {
        "categories_by_gmv_high",
        "categories_by_gmv_low",
    }:
        if wants_lowest(text):
            return categories_by_gmv(highest=False)

        if wants_highest(text):
            return categories_by_gmv(highest=True)

    if last_tool in {
        "delay_by_state_high",
        "delay_by_state_low",
    }:
        if wants_lowest(text):
            return delay_states(highest=False)

        if wants_highest(text):
            return delay_states(highest=True)

    if any(
        term in text
        for term in [
            "gmv",
            "pedidos",
        ]
    ):
        return executive_summary()

    return AgentResponse(
        tool="fallback",
        answer=(
            "Posso responder sobre datasets utilizados, "
            "KPIs gerais, categorias por GMV ou quantidade "
            "de pedidos, estados, taxas de atraso e "
            "pedidos específicos."
        ),
    )


def main():
    print("Olist Analytics Agent")
    print("Digite 'sair' para encerrar.")

    last_tool = None

    while True:
        question = input("\nVocê: ").strip()

        if normalize(question) in {
            "sair",
            "exit",
            "quit",
        }:
            break

        response = run_agent(
            question,
            last_tool=last_tool,
        )

        last_tool = response.tool

        print(f"\nFerramenta: {response.tool}")
        print(f"Agente: {response.answer}")


if __name__ == "__main__":
    main()
