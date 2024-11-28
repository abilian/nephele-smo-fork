.PHONY: all develop test lint clean doc format
.PHONY: clean clean-build clean-pyc clean-test coverage dist docs install lint lint/flake8

PKG:=smo

all:
	# Start with ruff because it's so fast
	uv run ruff check
	@make test
	@make lint

#
# Setup
#

## Install development dependencies and pre-commit hook (env must be already activated)
develop: install-deps activate-pre-commit configure-git

## Install dependencies
install-deps:
	@echo "--> Installing dependencies"
	uv sync

## Update dependencies
update-deps:
	@echo "--> Updating dependencies"
	uv sync -U
	uv pip list --outdated
	uv pip list --format=freeze > compliance/requirements-full.txt

## Generate SBOM
generate-sbom:
	@echo "--> Generating SBOM"
	uv sync -q --no-dev
	uv pip list --format=freeze > compliance/requirements-prod.txt
	uv sync -q
	# CycloneDX
	uv run cyclonedx-py requirements \
		--pyproject pyproject.toml -o compliance/sbom-cyclonedx.json \
		compliance/requirements-prod.txt
	# Add license information
	uv run lbom \
		--input_file compliance/sbom-cyclonedx.json \
		> compliance/sbom-lbom.json
	mv compliance/sbom-lbom.json compliance/sbom-cyclonedx.json
	# SPDX
	sbom4python -r compliance/requirements-prod.txt \
		--sbom spdx --format json \
		-o compliance/sbom-spdx.json

## Activate pre-commit hook
activate-pre-commit:
	@echo "--> Activating pre-commit hook"
	pre-commit install

## Configure git with autosetuprebase (rebase by default)
configure-git:
	@echo "--> Configuring git"
	git config branch.autosetuprebase always


#
# testing & checking
#

## Run python tests
test:
	@echo "--> Running Python tests"
	uv run pytest
	@echo ""

## Run python tests in random order
test-randomly:
	@echo "--> Running Python tests in random order"
	uv run pytest --random-order
	@echo ""

## Run end-to-end tests (not implemented yet)
test-e2e:
	@echo "--> Running e2e tests"
	@echo "TODO: not implemented yet"
	@echo ""

## Run tests with coverage
test-with-coverage:
	@echo "--> Running Python tests"
	uv run pytest --cov=${PKG} --cov-report term-missing
	@echo ""

## Run tests with typeguard
test-with-typeguard:
	@echo "--> Running Python tests with typeguard"
	uv run pytest --typeguard-packages=${PKG}
	@echo ""

## Run tests with beartype
test-with-beartype:
	@echo "--> Running Python tests with beartype"
	uv run pytest --beartype-packages=${PKG}
	@echo ""

## Lint / check typing
lint:
	# adt check
	uv run ruff check
	uv run flake8 src tests
	# mypy src
	# pyright src
	uv run deptry src

#
# Formatting
#

## Format / beautify code
format:
	uv run docformatter -i -r src
	uv run adt format
	uv run markdown-toc -i README.md


#
# Everything else
#

## Display this help
help:
	uv run adt help-make

## Cleanup repository
clean:
	adt clean
	rm -f **/*.pyc
	find . -type d -empty -delete
	rm -rf *.egg-info *.egg .coverage .eggs .cache .mypy_cache .pyre \
		.pytest_cache .pytest .DS_Store  docs/_build docs/cache docs/tmp \
		dist build pip-wheel-metadata junit-*.xml htmlcov coverage.xml

## Cleanup harder (you will need to re-install virtualenv and dependencies after this)
tidy: clean
	rm -rf .nox .venv
	rm -rf instance
