# SoulCare AI

Production-ready starter repository for **SoulCare**, an AI-powered mental wellness platform exploring multimodal emotion recognition and personalized stress support.

## What this starter includes

- FastAPI backend scaffold with versioned API routes
- Health endpoint for runtime checks
- Stress support check-in endpoint using multimodal input placeholders (`mood`, `text_signal`, `voice_signal`)
- Environment-driven configuration via `pydantic-settings`
- Test scaffolding with `pytest`
- Lint configuration with `ruff`
- Container starter via `Dockerfile`

## Quick start

### 1) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -e .[dev]
```

### 3) Configure environment

```bash
cp .env.example .env
```

### 4) Run API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5) Run tests

```bash
pytest
```

### 6) Run lint

```bash
ruff check .
```

## API surface

- `GET /health`: service status and environment
- `POST /v1/support/check-in`: accepts check-in payload and returns stress band + suggested action

Example request:

```json
{
  "mood": "overwhelmed",
  "stress_level": 8,
  "text_signal": "I am struggling to focus",
  "voice_signal": "rapid breathing"
}
```

## Safety note

SoulCare is intended for wellness support and is **not** an emergency or crisis response system.
