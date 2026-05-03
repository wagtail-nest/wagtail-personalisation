.PHONY: clean requirements develop test lint flake8 isort sandbox docs

default: develop

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
	isort src tests

sandbox:
	pip install -r sandbox/requirements.txt
	sandbox/manage.py migrate
	sandbox/manage.py loaddata sandbox/exampledata/users.json
	sandbox/manage.py loaddata sandbox/exampledata/personalisation.json
	sandbox/manage.py runserver
