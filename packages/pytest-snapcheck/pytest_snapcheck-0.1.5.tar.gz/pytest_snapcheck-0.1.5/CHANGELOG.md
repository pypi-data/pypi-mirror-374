# Changelog

All notable changes to this project are documented here. This project adheres to Semantic Versioning.

## [0.1.5] - 2025-09-06
- CI: Add tox and GitHub Actions workflow (pytest matrix + lint) ready for pytest-dev.
- Lint: Ruff and mypy lint env; scoped mypy to tests; adjusted Ruff ignores.
- Tests: Fixed plugin smoke test to avoid double-registration; tox now passing.
- Packaging: Include CHANGELOG in sdist; version bump; PyPI dist rebuild guidance.

## [0.1.4] - 2025-09-06
- Packaging: Added CHANGELOG.md and ensured it’s included in the source distribution.
- Build: Clean rebuild of distributions; metadata validation.

## [0.1.3] - 2025-09-05
- Published as `pytest-snapcheck` on PyPI.
- Kept CLI alias `pytest-snap` for backward compatibility.
- Added tox configuration and GitHub Actions CI (pytest matrix + lint).
- Packaging: ensured `py.typed` included; cleaned build warnings.
- Docs: README updates and PyPI description refresh guidance.

## [0.1.2] - 2025-09-05
- Renamed project to `pytest-snapcheck`; added `pytest-snapcheck` CLI alias.
- Improved CLI help and argument forwarding; removed example_suite references.
- Simplified MANIFEST and package data.

## [0.1.1] - 2025-09-04
- Added minimal smoke tests and initial CI pipeline.
- Improved diff features and help text.

## [0.1.0] - 2025-09-03
- Initial minimal pytest plugin to capture deterministic JSON snapshots.
- Basic CLI with run/diff utilities.
