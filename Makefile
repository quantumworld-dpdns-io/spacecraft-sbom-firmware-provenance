.PHONY: install dev install-all lint typecheck test test-unit test-integration \
        test-robot test-security coverage clean build docker-build docker-test \
        run migrate format security-scan pre-commit help

help:
	@echo "Targets:"
	@echo "  install         Install production dependencies"
	@echo "  dev             Install dev dependencies"
	@echo "  install-all     Install all dependencies"
	@echo "  lint            Run ruff linter"
	@echo "  format          Run ruff formatter"
	@echo "  typecheck       Run mypy type checker"
	@echo "  test            Run all tests"
	@echo "  test-unit       Run unit tests"
	@echo "  test-integration Run integration tests"
	@echo "  test-robot      Run Robot Framework tests"
	@echo "  test-security   Run security tests"
	@echo "  coverage        Run tests with coverage"
	@echo "  clean           Clean build artifacts"
	@echo "  build           Build package"
	@echo "  docker-build    Build Docker image"
	@echo "  docker-test     Run tests in Docker"
	@echo "  run             Start development server"
	@echo "  migrate         Run database migrations"
	@echo "  security-scan   Run security scanners"
	@echo "  pre-commit      Run pre-commit hooks"

install:
	pip install -r requirements/base.txt

dev: install
	pip install -r requirements/dev.txt

install-all: dev
	pip install -r requirements/test.txt
	pip install -r requirements/security.txt
	pip install -e ".[vector,analytics,ai]"

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

typecheck:
	mypy src/

test:
	pytest tests/ -v

test-unit:
	pytest tests/unit -v

test-integration:
	pytest tests/integration -v

test-robot:
	robot --outputdir tests/robot/output tests/robot/

test-security:
	bandit -r src/ -ll
	safety check --full-report

coverage:
	pytest tests/ --cov=src --cov-report=html --cov-report=xml --cov-report=term
	coverage report --fail-under=80

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf tests/robot/output/ coverage_html/ coverage.xml .coverage
	rm -rf bandit-report.json htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

build: clean
	python -m build

docker-build:
	docker build -t spacecraft-sbom-provenance:latest -f docker/Dockerfile .

docker-test:
	docker build -t spacecraft-sbom-provenance-test:latest -f docker/Dockerfile.test .
	docker run --rm spacecraft-sbom-provenance-test:latest

run:
	uvicorn src.sbom_provenance.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	alembic upgrade head

security-scan:
	bandit -r src/ -f json -o bandit-report.json
	safety check --full-report
	semgrep --config=auto src/

pre-commit:
	pre-commit run --all-files
