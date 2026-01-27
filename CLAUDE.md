# CLAUDE.md - AI Assistant Guide for docflow-cli

## Project Overview

**docflow-cli** is a production-ready Python CLI template for OCR + AI extraction pipelines. It's designed for ML engineers and automation developers who need:
- Deterministic AI stubs for testing
- Retryable pipeline orchestration
- Config validation with Pydantic
- Modular connectors for CRM/DMS integration

The CLI processes PDF documents through an OCR → AI extraction → CRM/DMS routing pipeline with SQLite audit logging.

## Directory Structure

```
docflow-cli/
├── .github/workflows/ci.yml    # GitHub Actions CI (lint, type check, test)
├── src/docflow/                # Main source package
│   ├── cli.py                  # Typer CLI commands (run, watch)
│   ├── pipeline.py             # Main orchestration with retry logic
│   ├── models.py               # Pydantic data models (Extraction, RunResult)
│   ├── config.py               # TOML config loading and validation
│   ├── ai.py                   # AI extraction (OpenAI or deterministic stub)
│   ├── ocr.py                  # OCR pipeline using ocrmypdf
│   ├── store.py                # SQLite run logging
│   └── connectors/
│       └── mock.py             # Mock CRM and DMS implementations
├── tests/
│   ├── test_config_validation.py
│   ├── test_pipeline_happy_path.py
│   └── golden/                 # Golden test fixtures
│       ├── sample_input.txt
│       └── expected_output.json
├── pyproject.toml              # Project config and dependencies
└── README.md
```

## Key Files and Their Responsibilities

| File | Purpose |
|------|---------|
| `src/docflow/cli.py` | Typer CLI with `run` (single PDF) and `watch` (directory monitor) commands |
| `src/docflow/pipeline.py` | Orchestrates OCR → AI → CRM → DMS flow with 3-retry exponential backoff |
| `src/docflow/models.py` | Defines `DocType`, `Extraction`, and `RunResult` Pydantic models |
| `src/docflow/config.py` | Loads and validates TOML config with Pydantic settings |
| `src/docflow/ai.py` | AI extraction with OpenAI API or deterministic stub mode (when no API key) |
| `src/docflow/ocr.py` | Runs ocrmypdf subprocess for PDF text extraction |
| `src/docflow/store.py` | SQLite logging of pipeline runs with start/finish timestamps |
| `src/docflow/connectors/mock.py` | Mock CRM (no-op) and DMS (file archiver) for testing |

## Development Setup

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Or install specific dependency groups
pip install -e .           # Runtime only
pip install -e ".[dev]"    # With pytest, ruff, mypy, etc.
```

**Python Version:** Requires Python 3.10+, targets 3.11 for mypy.

## Common Commands

### Running the CLI
```bash
docflow run config.toml document.pdf      # Process single PDF
docflow watch config.toml                 # Monitor inbox directory
```

### Development Commands
```bash
# Linting
ruff check .
ruff check --fix .           # Auto-fix issues

# Type checking
mypy src/docflow

# Testing
pytest                       # Run all tests
pytest --cov                 # With coverage
pytest --maxfail=1           # Stop on first failure
pytest -v                    # Verbose output

# All CI checks (matches GitHub Actions)
ruff check . && mypy src/docflow && pytest --cov --maxfail=1
```

## Code Conventions

### Style
- **Line length:** 100 characters (configured in ruff)
- **Python version:** 3.10+ syntax allowed
- **Imports:** Standard library, third-party, then local (ruff enforces)

### Type Hints
- All public functions should have type annotations
- Use Pydantic models for structured data
- `Literal` types for constrained strings (see `DocType`)

### Configuration
- TOML format for config files
- Pydantic models for validation in `config.py`
- Environment variables for secrets (e.g., `OPENAI_API_KEY`)

### Error Handling
- Use `tenacity` for retries with exponential backoff
- Pipeline failures are logged to SQLite with error details
- Status codes: `success`, `needs_review`, `failed`

### Testing Patterns
- Use `pytest` with `tmp_path` fixtures for file operations
- **Stub mode:** When `OPENAI_API_KEY` is unset, AI returns deterministic results
- Golden tests in `tests/golden/` for regression detection
- Monkeypatch environment variables for test isolation

## Architecture Patterns

### Pipeline Flow
```
PDF Input → OCR (ocrmypdf) → AI Extraction → CRM Record → DMS Archive → SQLite Log
```

### Retry Strategy
The pipeline uses `tenacity` with:
- 3 attempts maximum
- Exponential backoff: 1-8 seconds
- Configurable via decorators in `pipeline.py`

### Deterministic AI Stub
When `OPENAI_API_KEY` is not set, `ai.py` generates deterministic output using SHA-1 hash of input text. This ensures reproducible tests without API calls.

### Connector Architecture
Connectors (CRM, DMS) are pluggable:
- Interface: `record()` for CRM, `file()` for DMS
- Mock implementations in `connectors/mock.py`
- Select via config: `[connectors]` section in TOML

## CI/CD Pipeline

GitHub Actions runs on push/PR:
1. **Lint:** `ruff check .`
2. **Type check:** `mypy src/docflow`
3. **Test:** `pytest --cov --maxfail=1`

All checks must pass before merge.

## Data Models

### DocType
```python
Literal["RFP", "BID", "REBATE", "MSC", "ERR", "UNKNOWN"]
```

### Extraction (from AI)
```python
{
    "document_type": DocType,
    "summary": str,
    "required_actions": list[str],
    "notice_date": str | None,
    "amount": float | None,
    "confidence": float  # 0.0-1.0
}
```

### RunResult (pipeline output)
```python
{
    "run_id": str,           # UUID
    "status": str,           # success|needs_review|failed
    "input_pdf": Path,
    "output_pdf": Path,
    "extraction": Extraction | None,
    "error": str | None
}
```

## Configuration Format

Example TOML config:
```toml
[inbox]
pdf_dir = "/path/to/inbox"
archive_dir = "/path/to/archive"

[ocr]
engine = "ocrmypdf"
enabled = true

[ai]
provider = "openai"
model = "gpt-4o-mini"
api_key_env = "OPENAI_API_KEY"

[store]
db_path = "/path/to/runs.db"

[connectors]
crm = "mock"
dms = "mock"
```

## Known Issues and Notes

1. **Missing utils module:** `cli.py` imports `ensure_dir` from `docflow.utils` which doesn't exist yet
2. **OCR text extraction:** Currently returns empty string; actual text extraction is a placeholder
3. **Incomplete connectors:** Only mock implementations; HubSpot/Box mentioned in README but not implemented
4. **Watch mode:** Not currently tested in test suite

## When Making Changes

1. **Adding new modules:** Create in `src/docflow/`, add type hints, update this doc
2. **Adding dependencies:** Update `pyproject.toml` in appropriate section
3. **Adding connectors:** Implement in `src/docflow/connectors/`, follow mock.py pattern
4. **Adding tests:** Place in `tests/`, use `test_` prefix, leverage `tmp_path` fixture
5. **Modifying models:** Update `models.py`, ensure backward compatibility with golden tests

## Quick Reference

| Task | Command/Location |
|------|------------------|
| Run tests | `pytest` |
| Lint code | `ruff check .` |
| Type check | `mypy src/docflow` |
| CLI entry | `docflow` or `python -m docflow.cli` |
| Config models | `src/docflow/config.py` |
| Data models | `src/docflow/models.py` |
| Add connector | `src/docflow/connectors/` |
| Golden tests | `tests/golden/` |
