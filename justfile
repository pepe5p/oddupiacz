set dotenv-load

PYTHONPATH := "./oddupiacz"
PATHS_TO_LINT := "oddupiacz tests"
TEST_PATH := "tests"
ANSWERS_FILE := ".copier/.copier-answers.copier-python-project.yml"

[doc("Command run when 'just' is called without any arguments")]
default: help

[doc("Show this help message")]
@help:
	just --list

[group("development")]
[doc("Run all checks and tests (lints, mypy, tests...)")]
all: lint_full test

[group("development")]
[doc("Run all checks and tests, but fail on first that returns error (lints, mypy, tests...)")]
all_ff: lint_full_ff test

[group("lint")]
[doc("Run ruff lint check (code formatting)")]
ruff:
	uv run ruff check {{PATHS_TO_LINT}}
	uv run ruff format {{PATHS_TO_LINT}} --check

[group("copier")]
[doc("Update project using copier")]
copier_update answers=ANSWERS_FILE skip-answered="true":
	uv run copier update --answers-file {{answers}} \
	{{ if skip-answered == "true" { "--skip-answered" } else { "" } }}

[group("lint")]
[doc("Run fawltydeps lint check (deopendency issues)")]
deps:
	uv run fawltydeps

[group("lint")]
[doc("Run all lightweight lint checks (no mypy)")]
@lint:
	-just deps
	-just ruff

[group("lint")]
[doc("Run all lightweight lint checks, but fail on first that returns error")]
lint_ff: deps ruff

[group("lint")]
[doc("Automatically fix lint problems (only reported by ruff)")]
lint_fix:
	uv run ruff check {{PATHS_TO_LINT}} --fix
	uv run ruff format {{PATHS_TO_LINT}}

[group("lint")]
[doc("Run all lint checks and mypy")]
lint_full: lint mypy
alias full_lint := lint_full

[group("lint")]
[doc("Run all lint checks and mypy, but fail on first that returns error")]
lint_full_ff: lint_ff mypy
alias full_lint_ff := lint_full_ff

[group("lint")]
[doc("Run mypy check (type checking)")]
mypy: _set_pythonpath
	uv run mypy {{PATHS_TO_LINT}} --show-error-codes --show-traceback --implicit-reexport

[group("development")]
[doc("Open python console (useful when prefixed with dc, as it opens python console inside docker)")]
ps:
	PYTHONPATH={{PYTHONPATH}} uv run ipython
alias ipython := ps

[doc("Helper command, sets PYTHONPATH")]
_set_pythonpath path=PYTHONPATH:
	PYTHONPATH={{path}}

[group("development")]
[doc("Run non-integration tests (optionally specify file=path/to/test_file.py)")]
test file=TEST_PATH: _set_pythonpath
	uv run pytest {{file}} --durations=10
