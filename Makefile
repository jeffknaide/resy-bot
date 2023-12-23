clean:
	find . -name "*.pyc" -delete

poetry-config:
	poetry --version
	poetry config virtualenvs.in-project true

build: clean poetry-config
	poetry install -vvv

test:
	poetry run pytest tests/ --cov=resy_bot
	poetry run mypy resy_bot