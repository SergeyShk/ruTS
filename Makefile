.PHONY: clean clean-test clean-pyc clean-build ruff black isort mypy test check-code release-test release dist docs-build docs-serve docs-deploy help
.DEFAULT_GOAL := help
APP_PATH := ruts

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## Удалить все артефакты
	rm -f .coverage

clean-build: ## Удалить артефакты сборки
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	rm -fr target/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## Удалить артефакты компиляции
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## Удалить артефакты тестирования
	rm -fr .pytest_cache
	rm -fr .mypy_cache
	rm -fr .ruff_cache

ruff: ## Проверить код с помощью ruff
	poetry run ruff ${APP_PATH}

black: ## Форматировать код с помощью black
	poetry run black ${APP_PATH}

isort: ## Форматировать код с помощью isort
	poetry run isort ${APP_PATH}

mypy: ## Проверить код с помощью mypy
	poetry run mypy ${APP_PATH}

test: ## Запустить тесты
	poetry run pytest

check-code: ruff black isort test ## Запустить все проверки кода

release-test: dist ## Загрузить тестовый релиз
	poetry publish -r testpypi

release: dist ## Загрузить релиз
	poetry publish

dist: clean ## Собрать дистрибутив
	poetry build
	ls -l dist

docs-build: ## Собрать документацию
	rm -fr site/
	poetry run mkdocs build

docs-serve: ## Запустить сервер документации
	poetry run mkdocs serve

docs-deploy: ## Задеплоить документацию
	poetry run mkdocs gh-deploy