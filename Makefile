.PHONY: all clean test lint flake8 isort build

all: clean build

clean:
    find src -name '*.pyc' -delete
	find tests -name '*.pyc' -delete
	find . -name '*.egg-info' -delete

test:
    py.test --nomigrations --reuse-db tests/

lint: flake8 isort

flake8:
	pip install flake8 flake8-debugger flake8-blind-except
	flake8 src/

isort:
	pip install isort
	isort --recursive --check-only --diff src tests


build:
    ./setup.py sdist