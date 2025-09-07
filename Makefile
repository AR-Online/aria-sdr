.PHONY: up down build dev lint fmt type test smoke

up:
	docker compose --profile dev up --build

down:
	docker compose down -v

build:
	docker build -t aria-platform:dev .

dev:
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload

lint:
	ruff check . --fix

fmt:
	black .

type:
	pyright

test:
	pytest -q

smoke:
	pytest -q tests/test_smoke_api.py
