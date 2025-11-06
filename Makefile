.PHONY: setup dev prod install test clean

setup:
	bash scripts/setup_pi.sh

dev:
	bash scripts/run_all_dev.sh

prod:
	bash scripts/run_all_prod.sh

install:
	cd backend && pip install -e .
	cd detection-service && pip install -e .
	cd frontend && npm install

test:
	cd backend && pytest
	cd detection-service && pytest

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".venv" -exec rm -r {} +
	find . -type d -name "node_modules" -exec rm -r {} +

