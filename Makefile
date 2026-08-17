.PHONY: download build-bronze build-analytics train dashboard api agent lint test-mvp validate-mvp target-up target-down validate-foundation

PYTHON ?= python

download:
	$(PYTHON) scripts/data/download_olist.py

build-bronze:
	$(PYTHON) scripts/data/build_bronze.py

build-analytics:
	$(PYTHON) scripts/data/build_silver_gold.py

train:
	$(PYTHON) ml/src/olist_ml/train_delay_model.py

dashboard:
	$(PYTHON) -m streamlit run dashboard/app.py

api:
	$(PYTHON) -m uvicorn olist_api.main:app --app-dir api/src --port 8000

agent:
	$(PYTHON) agent/src/olist_agent/main.py

lint:
	$(PYTHON) -m ruff check agent/src/olist_agent/main.py api/src/olist_api/main.py dashboard/app.py ml/src/olist_ml/train_delay_model.py scripts/data/download_olist.py scripts/data/build_bronze.py scripts/data/build_silver_gold.py tests/integration/test_mvp_integration.py

test-mvp:
	$(PYTHON) -m pytest tests/integration/test_mvp_integration.py -q

validate-mvp: lint test-mvp

target-up:
	docker compose up -d postgres garage

target-down:
	docker compose down

validate-foundation:
	$(PYTHON) scripts/bootstrap/validate_m0.py
