SOURCE?=hyx docs/snippets
TESTS?=tests

.PHONY: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## Install project dependencies
	@uv sync --all-groups

clean: ## Clean temporary files
	@echo "Cleaning temporary files.."
	@rm -rf dist
	@rm -rf .mypy_cache .pytest_cache .ruff_cache
	@rm -rf .coverage htmlcov coverage.xml
	@rm -rf .mutmut-cache
	@rm -rf site

lint-check: ## Lint source code without modifying it
	@echo "Ruff check"
	@uv run ruff check $(SOURCE) $(TESTS)
	@echo "Ruff format"
	@uv run ruff format --check $(SOURCE) $(TESTS)
	@echo "MyPy"
	@uv run mypy --pretty $(SOURCE) $(TESTS)

lint: ## Lint source code
	@echo "Ruff check"
	@uv run ruff check --fix $(SOURCE) $(TESTS)
	@echo "Ruff format"
	@uv run ruff format $(SOURCE) $(TESTS)
	@echo "MyPy"
	@uv run mypy --pretty $(SOURCE) $(TESTS)

package-build: ## Build the project package
	@uv build

docs-serve: ## Start docs with autoreload
	@uv run mkdocs serve

docs-build: ## Build docs
	@uv run mkdocs build

build: package-build docs-build

test: ## Run tests
	@uv run coverage run -m pytest $(TESTS) $(SOURCE)

test-meta: ## Test robustness of the test suit
	@uv run mutmut run

test-meta-results: ## Show weak test cases
	@uv run mutmut results

test-cov-xml: ## Run tests
	@uv run coverage run -m pytest $(TESTS) --cov $(SOURCE) --cov-report=xml

test-cov-html: ## Generate test coverage
	@uv run coverage report --show-missing
	@uv run coverage html

test-cov-open: test-cov-html  ## Open test coverage in browser
	@open htmlcov/index.html
