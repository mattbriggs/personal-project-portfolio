# Portfolio Manager — Python Sidecar Backend

FastAPI sidecar for the Tauri desktop shell. Owns the domain logic, SQLite
persistence, migrations, and TOML configuration. Binds only to `127.0.0.1` on a
port supplied by the Rust supervisor, and requires a per-launch `X-API-Key`
token on every non-health route.

## Layout

```
src/portfolio_manager/
  domain/          framework-independent entities, enums, week/slug/scoring, errors
  application/     ports (Protocols) + services + DTOs
  infrastructure/  db (connection, schema, migrations, repositories, UoW),
                   config (TOML), logging, security, system (clock, paths)
  contracts/       Pydantic request/response/error models
  api/             FastAPI app factory, middleware, exception handlers, routes
  cli/             sidecar entry point
```

## Development

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest
.venv/bin/ruff check src tests
.venv/bin/mypy src
```

## Running the sidecar directly

```bash
PORTFOLIO_SIDECAR_TOKEN=dev-token \
  .venv/bin/python -m portfolio_manager.cli.sidecar --port 8765
curl -s 127.0.0.1:8765/health
curl -s -H "X-API-Key: dev-token" 127.0.0.1:8765/api/v1/projects
```

The token is read from `PORTFOLIO_SIDECAR_TOKEN` (env) or stdin — never from a
command-line argument, to keep it out of the process list.
