CHI TUI SDK (Python)

Typed Python CLI utilities for building command-line apps that emit a stable JSON envelope for terminal UIs. Uses Pydantic v2 and Click.

## Development

Install deps (dev extras included):

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e .[dev]
```

Run linters and tests manually:

```bash
ruff .
black --check .
pytest -q
```

### Pre-commit hooks

This repo includes pre-commit hooks for ruff, black, a max-lines check (<=600 lines per file), and pytest.

```bash
pre-commit install    # set up git hooks
pre-commit run -a     # run on all files once
```

Hooks run automatically on commit. The custom max-lines check applies to files under `src/` and `tests/`.
