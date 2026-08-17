# Governed Analytics Agent

**MVP status:** Implemented.

The current agent is deterministic and tool-driven. It provides governed analytical access to DuckDB without arbitrary SQL or administrative credentials.

Implemented capabilities:

- executive KPI summary;
- category rankings by GMV;
- category rankings by distinct order count;
- state rankings by GMV;
- highest/lowest delivery-delay rates;
- historical order lookup;
- limited contextual follow-up for rankings.

Run:

```powershell
.\.venv\Scripts\python.exe .\agent\src\olist_agent\main.py
```

The MVP does **not** claim an LLM-backed generative agent. LLM orchestration, prompt versioning, action tools and HITL remain target-architecture capabilities.
