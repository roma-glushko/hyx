SOURCE?=hyx
TESTS?=tests

clean: ## Clean temporary files
	@rm -rf dist
	@rm -rf .mypy_cache .pytest_cache

lint: ## Lint source code
	@echo "🧹 Ruff"
	@ruff --fix $(SOURCE) $(TESTS)
	@echo "🧽 MyPy"
	@mypy --pretty $(SOURCE) $(TESTS)

test: ## Run tests
	@coverage run -m pytest tests $(SOURCE)

test-cov: ## Generate test coverage
	@coverage report --show-missing
	@coverage html
	@open htmlcov/index.html