.PHONY: bootstrap up down ps validate-m0

bootstrap:
	python scripts/bootstrap/bootstrap_foundation.py

up:
	docker compose up -d postgres garage

down:
	docker compose down

ps:
	docker compose ps postgres garage

validate-m0:
	python scripts/bootstrap/validate_m0.py
