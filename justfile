# Task runner: https://github.com/casey/just
# Requires: `just`, Python virtualenv with dev dependencies.

# List all the justfile recipes.
default:
  just --list --list-prefix 'just '

# Remove Python file artifacts.
clean:
  find src -name '*.pyc' -delete
  find tests -name '*.pyc' -delete
  find . -name '*.egg-info' -exec rm -rf {} +

# Install dependencies for development.
requirements:
  pip install --upgrade -e .[docs,test]

# Install dependencies and clean.
develop: clean requirements

# Run the test suite.
test:
  pytest --reuse-db tests/

# Re-run tests with verbose output.
retest:
  pytest --reuse-db tests/ -vvv

# Run tests with coverage.
coverage:
  pytest --reuse-db tests/ --cov=wagtail_personalisation --cov-report=term-missing --cov-report=html

# Lint the project.
lint:
  pre-commit run --all-files

# Format Python files with ruff.
format *paths=".":
  uv run ruff check --fix {{paths}}
  uv run ruff format {{paths}}

# Build the documentation.
docs:
  mkdocs build --strict

# Build the documentation and serve it locally.
docs-serve:
  mkdocs serve --strict

# Set up and run the sandbox.
sandbox:
  pip install -r sandbox/requirements.txt
  sandbox/manage.py migrate
  sandbox/manage.py loaddata sandbox/exampledata/users.json
  sandbox/manage.py loaddata sandbox/exampledata/personalisation.json
  sandbox/manage.py runserver
