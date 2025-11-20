.PHONY: install run test clean help

help:
	@echo "Available targets:"
	@echo "  install  - Install the package with uv"
	@echo "  run      - Run example conversion"
	@echo "  test     - Run tests with pytest"
	@echo "  clean    - Remove build artifacts"

install:
	uv sync

run:
	uv run tomarkdown .

test:
	uv run pytest tests/ -v

clean:
	rm -rf .venv
	rm -rf *.egg-info
	rm -rf dist
	rm -rf build
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
