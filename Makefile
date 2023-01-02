SOURCE?=hyx docs/snippets
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
	@echo "🧹 Black"
	@black $(SOURCE) $(TESTS)
	@echo "🧽 MyPy"
	@mypy --pretty $(SOURCE) $(TESTS)

package-build: ## Build the project package
	@poetry build

docs-serve: ## Start docs with autoreload
	@poetry run mkdocs serve

docs-build: ## Build docs
	@poetry run mkdocs build

build: package-build docs-build

test: ## Run tests
	@poetry run coverage run -m pytest $(TESTS) $(SOURCE)

test-cov-xml: ## Run tests
	@poetry run coverage run -m pytest $(TESTS) --cov $(SOURCE) --cov-report=xml

test-cov-html: ## Generate test coverage
	@poetry run coverage report --show-missing
	@poetry run coverage html

test-cov-open: test-cov-html  ## Open test coverage in browser
	@open htmlcov/index.html
