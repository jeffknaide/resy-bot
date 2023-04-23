poetry-config:
	poetry --version
	poetry config virtualenvs.in-project true
	poetry config virtualenvs.path virtualenvs
	poetry env use python3.10

build: clean poetry-config
	poetry install -vvv

test:
	poetry run black --check resy_bot main.py
	poetry run pytest tests/ --cov=resy_bot
	poetry run mypy resy_bot main.py