# Contribution guidelines

Thank you for considering to help this project.

We welcome all support, whether on bug reports, code, design, reviews, tests, documentation, and more.

Please note that this project is released with a [Contributor Code of Conduct](https://wagtail.org/code-of-conduct/). By participating in this project you agree to abide by its terms.

## Development

### Installation

> Requirements: [just](https://github.com/casey/just), Python virtualenv.

Clone the repository:

```sh
git clone https://github.com/wagtail-nest/wagtail-personalisation.git
cd wagtail-personalisation
```

With your preferred virtualenv activated, install testing dependencies:

```sh
just develop
```

### Commands

- `just` – See what commands are available.
- `just develop` – Install dependencies and clean build artifacts.
- `just clean` – Remove Python file artifacts.
- `just test` – Run the full test suite.
- `just retest` – Re-run tests with verbose output.
- `just coverage` – Run tests with coverage report.
- `just lint` – Run all pre-commit checks.
- `just format *paths` – Format Python files with ruff (defaults to `.`).
- `just docs` – Build the documentation.
- `just docs-serve` – Build and serve the documentation locally.
- `just sandbox` – Set up and run the sandbox Wagtail site.

### Running tests

```sh
just test
```

or, you can run them for a specific environment with tox:

```sh
tox -e py314-dj60-wt74
```

or a specific test file:

```sh
tox -e py314-dj60-wt74 -- tests/unit/test_foo.py::test_bar
```

## Authors

- Jasper Berghoef
- Boris Besemer

## Contributors

- Michael van Tellingen
- Pim Vernooij
- Tomasz Knapik
- Kaitlyn Crawford
- Todd Dembrey
- Nathan Begbie
- Rob Moorman
- Tom Dyson
- Bertrand Bordage
- Alex Muller
- Saeed Marzban
- Milton Madanda
- Mike Dingjan
