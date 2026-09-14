# SoulCare AI

SoulCare AI is a FastAPI-based mental wellness support API starter with production-readiness controls.

## Canonical production runtime

- **Primary runtime:** Python 3.11 + FastAPI (`app/`)
- **Canonical API surface:** `GET /health`, `GET /ready`, `POST /v1/support/check-in`
- **Node starter (`src/`)** is retained for legacy reference and is not the production deployment target.

## Supported environments

- `local`: local development and integration tests
- `staging`: pre-production validation and release promotion checks
- `production`: public runtime with strict security and operations controls

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Required operational controls

- Environment-driven configuration via `SOULCARE_*` variables with validation
- Non-wildcard CORS in staging/production
- Request body size limits
- In-memory per-client rate limiting
- Idempotency support with `Idempotency-Key` on check-in endpoint
- Structured request logging with request IDs and no raw sensitive payload logging
- Safety escalation for high-risk self-harm language

## Python validation commands

```bash
ruff check .
pytest
python -m build
pip-audit
```

## Configuration

See `.env.example` for all configuration variables, including:

- app identity and environment (`SOULCARE_APP_*`)
- CORS policy (`SOULCARE_CORS_ALLOWED_ORIGINS`)
- request/rate/idempotency controls
- retention and incident contact fields

## CI/CD and release

- CI enforces lint, tests, build, dependency audit, secret scan, and container smoke checks
- Release workflow (tag-based) builds the container and publishes an SBOM artifact

## Governance and operations docs

- `/home/runner/work/soulcare-ai/soulcare-ai/PRODUCTION_READINESS.md`
