install: ## Sync the project with uv
	uv sync --group dev

lint:
	uv run --group dev isort --check .
	uv run --group dev black --check .
	uv run --group dev flake8 src tests

format: ## Formasts you code with Black
	uv run --group dev isort .
	uv run --group dev black .

test:
	uv run --group dev pytest -v tests

publish:
	uv build
	uv publish
