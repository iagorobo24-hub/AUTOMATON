.PHONY: help dev test test-backend test-frontend build clean run-backend run-frontend install-all

help:
	@echo "AUTOMATON Development Commands"
	@echo "  make install-all    Install project dependencies"
	@echo "  make dev            Run backend + frontend + Electron through root npm script"
	@echo "  make test           Run backend and frontend tests"
	@echo "  make build          Build frontend"
	@echo "  make clean          Remove local generated artifacts"

install-all:
	npm run install:all
	cd backend && pip install -r requirements.txt
	cd backend && pip install -r requirements-dev.txt

dev:
	npm run dev

test: test-backend test-frontend

test-backend:
	cd backend && pytest tests/ -v

test-frontend:
	cd frontend && npm test

build:
	cd frontend && npm run build

clean:
	rm -rf frontend/dist backend/.pytest_cache .pytest_cache .coverage htmlcov/ 2>/dev/null || true
	find backend -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	find backend -type f -name "*.pyc" -delete 2>/dev/null || true

run-backend:
	npm run dev:backend

run-frontend:
	npm run dev:frontend
