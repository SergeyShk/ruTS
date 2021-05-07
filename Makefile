.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

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

clean-build: ## Удалить артефакты сборки
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## Удалить артефакты компиляции
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## Удалить артефакты тестирования
	rm -fr .pytest_cache

lint: ## Проверить код с помощью flake8
	flake8 ruts tests

reformat: ## Форматировать код с помощью black
	black --line-length 99 ruts tests

test: ## Запустить тесты
	pytest

release-test: dist ## Загрузить тестовый релиз
	twine upload dist/* -r pypitest

release: dist ## Загрузить релиз
	twine upload dist/*

dist: clean ## Собрать дистрибутив
	python3 setup.py sdist
	python3 setup.py bdist_wheel
	ls -l dist

install: clean ## Установить дистрибутив
	python3 setup.py install

docs-build: ## Собрать документацию
	mkdocs build

docs-deploy: ## Задеплоить документацию
	mkdocs gh-deploy