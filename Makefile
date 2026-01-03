.PHONY: run test lint fmt clean

run:
	python3 server.py

test:
	PYTHONPATH=. python -m pytest -q

lint:
	ruff check .

fmt:
	ruff format .

clean:
	rm -rf .pytest_cache .ruff_cache __pycache__