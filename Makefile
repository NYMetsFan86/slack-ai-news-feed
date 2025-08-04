.PHONY: help install install-dev test lint type-check security-check clean deploy logs

help:
	@echo "Available commands:"
	@echo "  make install       Install production dependencies"
	@echo "  make install-dev   Install development dependencies"
	@echo "  make test         Run unit tests"
	@echo "  make lint         Run linting checks"
	@echo "  make type-check   Run type checking with mypy"
	@echo "  make security     Run security checks"
	@echo "  make clean        Clean up generated files"
	@echo "  make deploy       Deploy to Google Cloud Platform"
	@echo "  make logs         View Cloud Function logs"

install:
	pip install -r requirements.txt

install-dev: install
	pip install -r requirements-dev.txt

test:
	python -m pytest tests/ -v

lint:
	flake8 src/ tests/
	pylint src/ --disable=C0114,C0115,C0116,R0903

type-check:
	mypy src/

security:
	# Check for hardcoded secrets
	@echo "Checking for hardcoded secrets..."
	@! grep -r "sk-\|api_key.*=.*['\"]" src/ --include="*.py" || (echo "Found potential hardcoded secrets!" && exit 1)
	# Run bandit security scanner
	pip install bandit
	bandit -r src/ -ll
	# Check dependencies for vulnerabilities
	pip install safety
	safety check

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

deploy:
	./scripts/deploy_production.sh

logs:
	gcloud functions logs read ai-news-summarizer --limit=50

trigger:
	gcloud pubsub topics publish ai-news-trigger --message='{"test":true}'

# Development shortcuts
dev-test:
	python -m src.main

test-slack:
	python tests/quick_test.py

test-slack-interactive:
	python tests/test_slack_post.py

test-feeds:
	python tests/test_rss_feed.py

format:
	black src/ tests/

check-all: lint type-check security test
	@echo "All checks passed!"