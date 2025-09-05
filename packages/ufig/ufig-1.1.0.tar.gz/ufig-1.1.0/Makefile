.PHONY: tests coverage style-check docs help

help:
	@echo
	@echo "style-check - runs style checks on python files"
	@echo "tests       - runs test files in tests folder"
	@echo "coverage    - runs tests and determines test coverage"
	@echo "docs        - convert docs to html"

tests:
	uv run pytest -v tests/ $(ARGS)

coverage:
	NUMBA_DISABLE_JIT=1 uv run pytest -v --cov=src/ --color=yes --cov-report=html --cov-report=term tests/

style-check:
	uv run ruff check src/ tests/

docs:
	cd docs && uv run sphinx-build -b html . _build/html
