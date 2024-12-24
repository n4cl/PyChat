.PHONY: lint test all

all: lint test

lint:
	ruff check --output-format=github --config=ruff.toml

test:
	pytest
