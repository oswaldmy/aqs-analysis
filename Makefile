.PHONY: help install install-dev clean clean-pyc clean-build clean-pyenv lint test test-dbg develop mypy isort isort-check

install:
	python -m pip install -U pip setuptools pipenv
	python -m pipenv install


clean: clean-build clean-pyc

cleanall: clean clean-tox clean-sls clean-caches

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info
	rm -fr *.spec

clean-pyc:
	find . -name '*~' -exec rm -f {} +
	find . -name '*.log*' -delete
	find . -name '*_cache' -exec rm -rf {} +
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

clean-sls:
	rm -rf .serverless
	rm -rf node_modules

clean-tox:
	rm -rf .tox/

isort:
	tox -e isort

test:
	tox -e tests
