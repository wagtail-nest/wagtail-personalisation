.PHONY: all clean requirements develop test lint flake8 isort dist sandbox

all: clean requirements dist

default: develop

clean:
	find src -name '*.pyc' -delete
	find tests -name '*.pyc' -delete
	find . -name '*.egg-info' -delete

requirements:
	pip install --upgrade -e .[test]

install: develop

develop: clean requirements

test:
	py.test --nomigrations --reuse-db tests/

retest:
	py.test --nomigrations --reuse-db tests/ -vvv

coverage:
	py.test --nomigrations --reuse-db tests/ --cov=personalisation --cov-report=term-missing --cov-report=html

lint: flake8 isort

flake8:
	pip install flake8 flake8-debugger flake8-blind-except
	flake8 src/

isort:
	pip install isort
	isort --recursive src tests


dist:
	./setup.py sdist bdist_wheel


sandbox:
	pip install -r sandbox/requirements.txt
	sandbox/manage.py migrate
	sandbox/manage.py loaddata sandbox/exampledata/users.json 
	sandbox/manage.py runserver
