.PHONY: help dev test test-backend test-frontend lint build clean run-backend run-frontend install-all

help:
	@echo "AUTOMATON Development Commands"
	@echo ""
	@echo "  make install-all    Install all dependencies"
	@echo "  make dev            Run development mode (backend + frontend)"
	@echo "  make test           Run all tests"
	@echo "  make test-backend   Run backend tests"
	@echo "  make test-frontend Run frontend tests"
	@echo "  make lint          Run linters"
	@echo "  make build         Build for production"
	@echo "  make clean        Clean build artifacts"

install-all:
	cd backend && pip install -r requirements.txt
	cd backend && pip install -r requirements-dev.txt
	cd frontend && npm install

dev:
	@echo "Starting backend..."
	cd backend && uvicorn app.main:app --reload --port 8000
	@echo "Starting frontend..."
	cd frontend && npm run dev

test:
	make test-backend
	make test-frontend

test-backend:
	cd backend && pytest tests/ -v

test-frontend:
	cd frontend && npm test

lint:
	cd backend && ruff check app/
	cd backend && black --check app/
	cd frontend && npm run lint

build:
	cd frontend && npm run build
	@echo "Build complete"

clean:
	cd backend && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	cd backend && find . -type f -name "*.pyc" -delete 2>/dev/null || true
	cd frontend && npm run clean
	rm -rf .coverage htmlcov/ 2>/dev/null || true

run-backend:
	cd backend && uvicorn app.main:app --reload --port 8000

run-frontend:
	cd frontend && npm run dev