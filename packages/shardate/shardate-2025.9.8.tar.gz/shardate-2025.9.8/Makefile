lint:
	uv run ruff check --fix .
	uv run ruff format .
	
clean:
	rm -rf .mypy_cache
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf artifacts
	rm -rf .ruff_cache
	rm -rf .venv
	rm -f uv.lock
	find . -name '__pycache__' -exec rm -rf {} +

build:
	uv run python -m build

publish: build
	uv run twine upload dist/*

publish-test:
	uv run twine upload --repository testpypi dist/*

test:
	uv run pytest -vvv
