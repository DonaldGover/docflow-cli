# docflow-cli — AI Pipeline CLI Template

A production-ready Python CLI for **OCR + AI extraction** pipelines — built with a focus on
**testing, reproducibility, and infrastructure reliability**.

Designed for ML engineers and automation developers who need:
- Deterministic AI stubs for testing
- Retryable pipeline orchestration
- Config validation with Pydantic
- Modular connectors for CRM/DMS or ML backends

---

## 🚀 Features
- CLI built with **Typer**
- **Config validation** (Pydantic + TOML)
- **Retries + exponential backoff** (Tenacity)
- **Golden tests** for reproducible AI outputs
- **SQLite run log** for traceability
- **GitHub Actions CI** (Ruff + Mypy + Pytest + Coverage)
- **Pluggable connectors** (HubSpot, Box, Mock)
