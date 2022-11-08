.PHONY: all clean requirements develop test lint flake8 isort dist sandbox docs

default: develop

all: clean requirements dist

clean:
	find src -name '*.pyc' -delete
	find tests -name '*.pyc' -delete
	find . -name '*.egg-info' |xargs rm -rf

requirements:
	pip install --upgrade -e .[docs,test]

install: develop

develop: clean requirements

test:
	py.test --reuse-db tests/

retest:
	py.test --reuse-db tests/ -vvv

coverage:
	py.test --reuse-db tests/ --cov=wagtail_personalisation --cov-report=term-missing --cov-report=html

docs:
	$(MAKE) -C docs html

lint: flake8 isort

flake8:
	flake8 src/ tests/

isort:
	pip install isort
	isort --recursive src tests

dist:
	pip install wheel
	python ./setup.py sdist bdist_wheel

sandbox:
	pip install -r sandbox/requirements.txt
	sandbox/manage.py migrate
	sandbox/manage.py loaddata sandbox/exampledata/users.json
	sandbox/manage.py loaddata sandbox/exampledata/personalisation.json
	sandbox/manage.py runserver

release:
	pip install twine wheel
	rm -rf dist/*
	python setup.py sdist bdist_wheel
	twine upload -s dist/*


test-215:
	tox -e py38-dj32-wt215

test-30:
	tox -e py38-dj40-wt30

test-40:
	tox -e py38-dj40-wt40

test-41:
	tox -e py38-dj41-wt41
