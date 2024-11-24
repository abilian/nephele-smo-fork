# SMO

This repository hosts the Synergetic Meta-Orchestrator consisting of a Flask REST API that is responsible for translating intent formulations, constructing and enforcing deployment plans for Hyper Distributed Application Graphs.

This is a fork of the original SMO repository, which can be found [here](https://gitlab.eclipse.org/eclipse-research-labs/nephele-project/smo).

Build status: [![builds.sr.ht status](https://builds.sr.ht/~sfermigier/smo.svg)](https://builds.sr.ht/~sfermigier/smo?)

## TOC

<!-- toc -->

  * [Changes from the Original Repository](#changes-from-the-original-repository)
  * [Current Status and Issues](#current-status-and-issues)
  * [Getting started](#getting-started)
    + [Prerequisites](#prerequisites)
    + [Using Python](#using-python)
    + [Using Docker](#using-docker)
    + [Using docker-compose](#using-docker-compose)
    + [Using Vagrant](#using-vagrant)
  * [Changelog from the Original Repository](#changelog-from-the-original-repository)
    + [DONE](#done)
    + [TODO / Roadmap](#todo--roadmap)
  * [Contributing](#contributing)
    + [Setting up the development environment](#setting-up-the-development-environment)
      - [Prerequisite: `uv`](#prerequisite-uv)
      - [Setting up the environment](#setting-up-the-environment)
    + [Tooling](#tooling)
    + [Contribution Guidelines](#contribution-guidelines)
    + [Code Style](#code-style)
    + [Testing](#testing)
      - [`pytest`](#pytest)
    + [Documentation](#documentation)
    + [Pull Request Process](#pull-request-process)
    + [Code of Conduct](#code-of-conduct)
  * [Deployment](#deployment)
    + [On Hop3](#on-hop3)
    + [On Heroku](#on-heroku)
    + [On Docker Swarm](#on-docker-swarm)
- [Original README](#original-readme)
  * [Getting started](#getting-started-1)
  * [File structure](#file-structure)

<!-- tocstop -->

## Changes from the Original Repository

This repository has undergone a few changes to enhance its functionality, maintainability and compatibility.

1**Introduction of `pyproject.toml`**: This repository has been updated to reflect a [post-hypermodern Python development approach](https://rdrn.me/postmodern-python/). The adoption of a `pyproject.toml` file provides a standardized and centralized configuration for dependency management and tooling. This simplifies project setup, ensures compatibility with modern Python packaging standards, and consolidates configuration for tools such as linters, formatters, and test runners.

2**Project Refactoring**: The codebase has been reorganized to improve readability, remove unnecessary dependencies, and simplify the overall structure. This ensures a cleaner and more maintainable implementation.

3**Database Support**: Added support for SQLite, enabling more flexibility in deployment environments and simplifying testing and development setups.

4**Namespace Introduction**: A dedicated namespace for the SMO has been introduced to better organize the project and facilitate integration with other components in the open-source cloud ecosystem (including [Hop3](https://github.com/abilian/hop3)).

5**Continuous Integration Enhancements**: We've created a CI pipeline to ensure smoother automated testing, formatting enforcement, and build processes.

6**Code Quality Improvements**: Static analysis (ruff, flake8, mypy, pyright...) and formatting (ruff, black, isort...) tools have been implemented to ensure consistent coding standards, and some minor issues and warnings have been resolved.

7**Testing Additions**: We have added basic unit tests to validate functionality and improve the reliability of the codebase.

8**Documentation Updates**: Additional documentation (this README) has been included to clarify the usage and contribution guidelines for the project.

## Current Status and Issues

The current version of the SMO project is a **work in progress**, with several planned enhancements and improvements. The following are some of the key areas that we are actively working on:

- **Dependency Issue**: The current deployment mechanism relies on `hdarctl`, which is not universally compatible. We are exploring alternative solutions to address this dependency issue and ensure broader compatibility.
- **Test Coverage**: While we have added a few basic unit tests, current coverage rate is only 48%, which is quite low. We are working to expand test coverage to include integration tests and end-to-end tests to validate the functionality of the application more comprehensively.
- **Configuration Management**: Currently the configuraion is hardwired. We are enhancing the configuration management system to provide more flexibility and customization options for deployment environments.
- **Error Handling and Logging**: We are enhancing error handling and logging mechanisms to improve the robustness and reliability of the application.
- **Refactoring and Modernization**: We are refactoring the codebase to use modern Python features and best practices, including the adoption of a layered architecture, improved configuration management, and dependency injection mechanisms.
- **Type Annotations**: We are adding type hints to all functions and methods to improve code readability and maintainability.
- **Linting and Formatting**: We are addressing all linting and type-checking issues to ensure consistent code quality and adherence to coding standards.
- **Documentation Improvements**: We are updating the documentation to include a changelog, improve readability, and provide more comprehensive information on the project.
- **Changelog**: We are introducing a changelog to track changes and updates to the project more effectively.
- **CI/CD Pipeline**: We are enhancing the CI/CD pipeline to automate testing, linting, and formatting processes more efficiently.
- **Deployment Options**: We are exploring deployment options on various platforms, including Hop3, Heroku, and Docker Swarm, to provide more flexibility and scalability.
- **Contributions**: We welcome contributions from the community to help us address these issues and improve the SMO project further.
- **License**: The original SMO repository is licensed under the MIT License. We are maintaining the same license for this fork to ensure compliance with the original project's licensing terms.
- **Licensing Issues**: The project uses the Gurobi Optimizer which is a mathematical optimization software library for solving mixed-integer linear and quadratic optimization problems. This package comes with a trial license that allows to solve problems of limited size. We need to replace it with an open-source alternative to avoid licensing issues.

## License

The original SMO repository is licensed under the MIT License. We are maintaining the same license for this fork to ensure compliance with the original project's licensing terms.

### License Compliance

Here is the license compliance report (`reuse lint`) for this repository:

```
* Bad licenses: 0
* Deprecated licenses: 0
* Licenses without file extension: 0
* Missing licenses: 0
* Unused licenses: 0
* Used licenses: BSD-3-Clause, CC-BY-4.0, MIT
* Read errors: 0
* Files with copyright information: 48 / 48
* Files with license information: 48 / 48

Congratulations! Your project is compliant with version 3.3 of the REUSE Specification :-)
```

### Third-Party Licenses

Note that third party libraries used in this project may have different licenses. Please refer to the respective libraries' documentation for details. We will provide a more detailed assessment of third-party licenses in the future.

This is especially relevant for the Gurobi Optimizer, which is a mathematical optimization software library for solving mixed-integer linear and quadratic optimization problems. This package comes with a trial license that allows to solve problems of limited size. As stated elswhere, we need to replace it with an open-source alternative to avoid licensing issues.


## Getting started

### Prerequisites

> [!NOTE]
> We currently rely on `[hdarctl](https://gitlab.eclipse.org/eclipse-research-labs/nephele-project/nephele-hdar.git)` for the deployment of applications. A binary is currently provided in this repository, but it will only work on Linux/x86_64 (for other architecture, you will have to build another binary). We need to find a more robust solution.

### Using Python

Assuming you have a working Python environment, you can install the dependencies and run the application as follows:

```bash
# Install for development
pip install -e .
# ... or for production
pip install .
# Run the application
flask run
```

### Using Docker

```bash
docker build -t smo .
docker run -p 5000:5000 smo
```

> [!WARNING]
> This will run the application in debug mode. DO NOT use this in production.

### Using docker-compose

```bash
docker-compose up
```

> [!WARNING]
> This will run the application in debug mode. DO NOT use this in production.

### Using Vagrant

```bash
vagrant up
vagrant ssh
# etc.
```

## Changelog from the Original Repository

### DONE

- [x] Refactor codebase for readability and maintainability.
- [x] Remove unnecessary dependencies.
- [x] Add SQLite support for database flexibility.
- [x] Introduce SMO-specific namespace for better organization.
- [x] Add basic unit tests for functionality validation.
- [x] Implement static analysis and enforce consistent formatting.
- [x] Create a CI pipeline on SourceHut.
- [x] Update documentation for usage and contribution guidelines (README)
- [x] Extend test capabilities to include runtime type-checking with tools like **Typeguard** and **Beartype**.
- [x] Introduce a `Makefile` to streamline hypermodern Python development workflows (e.g., testing, linting, formatting).
- [x] Add support for local development with **Vagrant**.
- [x] Enable easy integration and deployment with **Heroku**.

### TODO / Roadmap

- [ ] fix: Work around the `hdarctl` dependency issue.
- [ ] test: Add more unit tests in order to reach close to 100% coverage.
- [ ] test: Add integration tests.
- [ ] test: Add e2e tests.
- [ ] test: test Swagger API using [Schemathesis](https://github.com/schemathesis/schemathesis?tab=readme-ov-file) (and/or [Bravado](https://pypi.org/project/pytest-bravado/)). (Not Dredd - Dredd is dead, killed by Oracle)
- [ ] feature: Improve error handling and logging.
- [ ] refact: use the modern (2.0) SQLAlchemy ORM API.
- [ ] refact: Refactor using a layered architecture.
- [ ] refact: Implement a proper configuration management.
- [ ] refact: Implement a dependency injection mechanism.
- [ ] refact: Replace the Gurobi Optimizer with an open-source alternative (or make the optimizer pluggable).
- [ ] type: Add type hints to all functions and methods.
- [ ] lint: Fix / suppress all linting issues (ruff, flake8).
- [ ] lint: Resolve all type-checking issues (mypy, pyright, typeguard, beartype).
- [ ] doc: Introduce a Changelog (and tools to manage it, like `towncryer` or similar).
- [ ] doc: Create a proper documentation site using markdown-material
- [ ] chore: Add a license compliance report (and double-check REUSE config).

## Contributing

We welcome contributions to the SMO project! Below is a guide to help you get started.

### Setting up the development environment

#### Prerequisite: `uv`

We recommend to use `uv`, which is a rapidly evolving Python project that aims to provide a modern, flexible, and efficient way to manage Python environments. It is designed to be a drop-in replacement for `virtualenv`, `pyenv`, `pipenv`, `poetry`, `rye`.

If `uv` is not supported by your OS (with Homebrew or Linuxbrew, you can install it with `brew install uv`, and you can similarly leverage Nix or Guix to get a recent version of `uv`), you can use `pipx` to install it (assuming you have `pipx` installed, of course):

```bash
pipx install uv
```

Or simply:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or on Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Setting up the environment

```bash
uv venv
. .venv/bin/activate
uv sync
```

### Tooling

Besides the `uv` tool, we use the following tools to maintain the codebase:

- **ruff**: A modern, flexible, and efficient way to manage Python environments.
- **black**: The uncompromising Python code formatter.
- **isort**: A Python utility / library to sort imports.
- **flake8**: A Python tool that glues together pep8, pyflakes, mccabe, and third-party plugins to check the style and quality of some Python code.
- **mypy**: An optional static type checker for Python.
- **pyright**: A static type checker for Python that runs in the background.
- **pytest**: A framework that makes it easy to write small tests, yet scales to support complex functional testing for applications and libraries.
- **beartype**: A runtime type-checker for Python functions.
- **typeguard**: Run-time type checking for Python functions.
- **nox**: A flexible test automation tool that automates testing in multiple Python environments.

We orchestrate these tools using `make`, the standard build tool on Unix-like systems, which provides shortcuts for common tasks based on these tools:

The provided `Makefile` orchestrates various tasks to streamline development, testing, formatting, and maintenance workflows. Here’s a high-level overview of the key functionalities it provides:

- **`develop`**: Installs development dependencies, activates pre-commit hooks, and configures Git for rebase workflows by default.
- **`install-deps`**: Ensures the project's dependencies are synced and up-to-date using `uv sync`.
- **`update-deps`**: Updates the project's dependencies to the latest compatible versions using `uv sync -U`.
- **`activate-pre-commit`**: Installs pre-commit hooks to automatically enforce coding standards during commits.
- **`configure-git`**: Sets Git to use rebase workflows automatically when pulling branches.
- **`test`**: Runs Python unit tests using `pytest`.
- **`test-randomly`**: Executes tests in a randomized order to uncover order-dependent issues.
- **`test-e2e`**: Placeholder for running end-to-end tests (not yet implemented).
- **`test-with-coverage`**: Runs tests and generates a coverage report for the specified package.
- **`test-with-typeguard`**: Verifies runtime type checking for the package using `Typeguard`.
- **`lint`**: Performs linting and type-checking using `adt check` to ensure code quality.
- **`format`**: Formats code to meet the style guide using `docformatter` for documentation strings and `adt format` for general formatting.
- **`clean`**: Cleans up temporary files, cache directories, and build artifacts, leaving the repository in a pristine state.
- **`help`**: Displays available `make` commands and their descriptions, leveraging `adt help-make`.

The full list of available commands can be viewed by running `make help`.


### Contribution Guidelines

1. **Fork the Repository**: Create a fork of the repository in your own GitHub/GitLab account.
2. **Create a Feature Branch**: Make a new branch in your fork for the feature or bugfix you plan to work on.
3. **Follow the Code Style**: Adhere to the project's code style guidelines (see below).
4. **Add Tests**: Ensure your changes are covered by appropriate unit and integration tests.
5. **Document Changes**: Update relevant sections in the documentation, including this README if necessary.
6. **Submit a Pull Request**: Open a pull request against the `main` branch of this repository with a clear description of your changes.

### Code Style

We use **PEP 8** as the basis for our code style, with additional configurations provided by:

- **Black**: Ensures consistent formatting.
- **Ruff**: Handles linting and static analysis.
- **isort**: Organizes imports.

To apply formatting and linting, simply run:

```bash
ruff . --fix
black .
isort .
```

Or, better yet, use the provided `Makefile` shortcuts:

- `make format`: Apply formatting.

### Testing

Tests are critical to maintaining the quality and reliability of the codebase. We encourage contributors to:

- Add **unit tests** for new or modified functionalities.
- Write **integration tests** for changes that affect multiple components.


#### `pytest`

Run all tests using:

```bash
pytest
```

For test coverage, use:

```bash
pytest --cov=smo
```

The `Makefile` provides shortcuts for common testing tasks:

- `make test`: Run all tests.
- `make test-randomly`: Run tests in random order.
- `make test-with-coverage`: Run tests with coverage report.
- `make test-with-typeguard`: Run tests with typeguard enabled.
- `make test-with-beartype`: Run tests with beartype enabled.
- `make lint`: Run linters and static analysis.

#### `nox`

We use `nox` to automate testing in multiple Python environments. To run tests with `nox`, use:

```bash
nox
```

(Run `nox -l` to list available session types.)

### Documentation

All new features or changes should be documented. The documentation should include:

- **Code Comments**: Explain non-trivial parts of the code.
- **README Updates**: Update this file for any major changes in functionality or usage.
- **Changelog**: Add a note in the upcoming changelog (to be implemented).
- **API Documentation**: Update the API documentation if necessary (swagger files).

### Pull Request Process

To ensure a smooth review process:

1. Make sure your branch is **up to date** with the `main` branch.
2. Ensure all tests pass and there are no linting or formatting issues.
3. Provide a clear and concise description of the changes in your pull request, including any relevant issue numbers.
4. Be responsive to reviewer feedback and address any requested changes promptly.


### Code of Conduct

This project adheres to the [PSF Code of Conduct](https://policies.python.org/python.org/code-of-conduct/). By participating, you agree to abide by its terms. Please be respectful and collaborative in all interactions.

For further details, see the `[CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)` file in the repository.


## Deployment

### On Hop3

```bash
hop create smo
hop deploy smo
# TODO: env vars
```

### On Heroku

```bash
heroku create
heroku addons:create heroku-postgresql:essential-0
heroku config:set FLASK_APP=smo
heroku config:set FLASK_ENV=production
# TODO: set SQLALCHEMY_DATABASE_URI properly
git push heroku main
heroku run flask db upgrade
```

### On Docker Swarm

TODO.

---

# Original README

## Getting started
Use docker compose:
```
docker-compose up
```
The SMO API is available at port 8000.

## File structure
The directory structure of the codebase is as follows:
```
src/
├── errors
├── models
├── routes
├── services
├── utils
├── app.py
└── config.py
```
- `errors`: custom errors and handlers
- `models`: db models
- `routes`: app blueprints
- `services`: business logic for the routes
- `utils`: misc
- `app.py`: the Flask application
- `config.py`: the Flask application configuration files
