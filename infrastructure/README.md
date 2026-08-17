# Infrastructure

**Runtime status:** Target architecture scaffold.

The repository retains Docker Compose, Garage and PostgreSQL foundation assets from the original architecture.

The executable MVP adopted by ADR-0009 runs Windows-native with:

- Python 3.12;
- local filesystem and Parquet;
- DuckDB;
- Streamlit;
- MLflow with SQLite;
- FastAPI.

Docker, Garage and PostgreSQL are therefore preserved for future architecture evolution and are not required to run the current MVP.
