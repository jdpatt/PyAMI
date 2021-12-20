.PHONY: all lint format tests clean

all: format tests lint

lint:
	pylint pyibisami/ tests/; mypy -p pyibisami --ignore-missing-imports

format:
	autoflake --in-place --remove-all-unused-imports --expand-star-imports \
	--ignore-init-module-imports --recursive pyibisami/ tests/; isort pyibisami/ tests/; black pyibisami/ tests/

tests:
	pytest -vv -n 4 --disable-pytest-warnings tests/

clean:
	rm -rf .pytest_cache .tox htmlcov *.egg-info .coverage
