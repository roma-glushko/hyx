SOURCE?=hyx docs/snippets
TESTS?=tests

.PHONY: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## Install project dependencies
	@poetry install

clean: ## Clean temporary files
	@echo "🧹 Cleaning temporary files.."
	@rm -rf dist
	@rm -rf .mypy_cache .pytest_cache .ruff_cache
	@rm -rf .coverage htmlcov coverage.xml
	@rm -rf .mutmut-cache
	@rm -rf site

lint-check: ## Lint source code without modifying it
	@echo "🧹 Ruff"
	@poetry run ruff $(SOURCE) $(TESTS)
	@echo "🧹 Black"
	@poetry run black --check $(SOURCE) $(TESTS)
	@echo "🧽 MyPy"
	@poetry run mypy --pretty $(SOURCE) $(TESTS)

lint: ## Lint source code
	@echo "🧹 Ruff"
	@poetry run ruff --fix $(SOURCE) $(TESTS)
	@echo "🧹 Black"
	@poetry run black $(SOURCE) $(TESTS)
	@echo "🧹 Ruff"
	@ruff --fix $(SOURCE) $(TESTS)
	@echo "🧽 MyPy"
	@poetry run mypy --pretty $(SOURCE) $(TESTS)

package-build: ## Build the project package
	@poetry build

docs-serve: ## Start docs with autoreload
	@poetry run mkdocs serve

docs-build: ## Build docs
	@poetry run mkdocs build

build: package-build docs-build

test: ## Run tests
	@poetry run coverage run -m pytest $(TESTS) $(SOURCE)

test-meta: ## Test robustness of the test suit
	@mutmut run

test-meta-results: ## Show weak test cases
	@mutmut results

test-cov-xml: ## Run tests
	@poetry run coverage run -m pytest $(TESTS) --cov $(SOURCE) --cov-report=xml

test-cov-html: ## Generate test coverage
	@poetry run coverage report --show-missing
	@poetry run coverage html

test-cov-open: test-cov-html  ## Open test coverage in browser
	@open htmlcov/index.html
