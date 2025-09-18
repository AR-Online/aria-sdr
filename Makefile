.PHONY: up down build dev lint fmt type test smoke deps-dev test-local

# Default base URL used by tests (prefer 127.0.0.1 for Windows stability)
BASE_URL ?= http://127.0.0.1:8000

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
	$(MAKE) deps-dev
	BASE_URL=$(BASE_URL) pytest -q

smoke:
	$(MAKE) deps-dev
	BASE_URL=$(BASE_URL) pytest -q tests/test_smoke_api.py

deps-dev:
	python -m pip install -r requirements.txt -r requirements-dev.txt

test-local:
	$(MAKE) deps-dev
	pytest -q tests/test_thread_id_precedence.py
