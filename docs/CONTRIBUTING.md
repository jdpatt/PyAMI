# Contributing

## Fork/Pull Requests

1. Fork the repository to your own Github account
2. Clone the project to your machine
3. Create a branch locally with a succinct but descriptive name
4. Commit changes to the branch
5. Following any formatting and testing guidelines specific to this repo
6. Push changes to your fork
7. Open a PR in our repository and follow the PR template so that we can efficiently review the changes.

## Tooling

The `Makefile` has most of these commands or features for easy use across developers.  Install the
optional developer tooling run `pip install -r requirements_dev.txt` which conda will install them
via pip into the current environment.  The most useful one is simply `make all` which will test,
format and lint.

### Linting

Currently, pybert loosely uses pylint and mypy to catch glaring issues. You can run both with `make lint`.

### Formatting

Formatting in controlled in the `pyproject.toml` file and running `make format` will run autoflake,
isort and black against the codebase.

### Testing

Pytest is used for the test runner and documentation builder. Both pybert's and pyibisami's test suite
will be run with `make tests`.
