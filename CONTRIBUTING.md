# Contributing to nodus-adapters

## Setup (base package)

```bash
cd base
pip install -e ".[dev]"
pytest tests/ -q
```

## Adding a new adapter package

1. Create `adapters/<name>/` with `pyproject.toml`, `nodus_adapter_<name>/`, and `tests/`
2. Extend `BaseChannelAdapter` from `nodus-adapter-base`
3. Add the new package to the table in the root `README.md`
4. Ensure `pytest tests/ -q` passes before opening a PR

## Code style

- Python 3.11+
- Type hints on all public methods
- `asyncio_mode = "auto"` in `pyproject.toml` for async tests

## Submitting changes

1. Fork the repo and create a branch from `main`
2. Add tests for any new behaviour
3. Open a pull request with a description of what changes and why
