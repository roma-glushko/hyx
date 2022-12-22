SOURCE?=hyx
TESTS?=tests

clean: ## Clean temporary files
	@echo "🧹 Cleaning temporary files.."
	@rm -rf dist
	@rm -rf .mypy_cache .pytest_cache .ruff_cache
	@rm -rf .coverage htmlcov
	@rm -rf site

lint: ## Lint source code
	@echo "🧹 Ruff"
	@ruff --fix $(SOURCE) $(TESTS)
	@echo "🧽 MyPy"
	@mypy --pretty $(SOURCE) $(TESTS)

package-build: ## Build the project package
	@poetry build

docs-serve: ## Start docs with autoreload
	@poetry run mkdocs servce

docs-build: ## Build docs
	@poetry run mkdocs build

build: package-build docs-build

test: ## Run tests
	@poetry run coverage run -m pytest tests $(SOURCE)

test-cov: ## Generate test coverage
	@poetry run coverage report --show-missing
	@poetry run coverage html
	@open htmlcov/index.html