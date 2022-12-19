SOURCE?=hyx
TESTS?=tests

clean: ## Clean temporary files
	@rm -rf dist
	@rm -rf .mypy_cache .pytest_cache

lint: ## Lint source code
	@mypy --pretty $(SOURCE) $(TESTS)