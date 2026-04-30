.PHONY: install test clean web lint format docs

install:
	pip install -e .

test:
	pytest tests/ -v

clean:
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

web:
	ghostdump --web --port 8080

lint:
	flake8 ghostdumper/ tests/
	mypy ghostdumper/

format:
	black ghostdumper/ tests/

docs:
	@echo "Documentation is in docs/ directory"

termux:
	python ghostdumper/scripts/termux_setup.py
