# SoulCare AI Starter

SoulCare is an AI-powered mental wellness platform exploring multimodal emotion recognition and personalized stress support through research-driven technology.

This repository provides a production-ready starter backend focused on secure defaults, observability-ready logs, automated tests, and CI.

## Features

- Node.js HTTP API starter with no third-party runtime dependencies
- `GET /health` health endpoint for service monitoring
- `POST /v1/support-plan` stress support recommendation endpoint
- Environment-based configuration with required-variable validation
- Security-oriented response headers and request-size limits
- JSON structured logs for operations and tracing
- Docker image definition for container deployment
- GitHub Actions workflow for automated test validation

## Quick Start

### 1) Prerequisites

- Node.js 20+

### 2) Setup

```bash
cp .env.example .env
npm install
```

### 3) Run locally

```bash
NODE_ENV=development npm run dev
```

The API will start on `http://localhost:3000` by default.

## API Endpoints

### `GET /health`
Returns platform status metadata.

Example response:

```json
{
  "status": "ok",
  "service": "soulcare-api",
  "environment": "development",
  "timestamp": "2026-01-01T00:00:00.000Z"
}
```

### `POST /v1/support-plan`
Generates a starter stress support plan from a user payload.

Example request:

```json
{
  "userId": "user-123",
  "stressScore": 0.72
}
```

Example response:

```json
{
  "userId": "user-123",
  "stressScore": 0.72,
  "stressLevel": "high",
  "recommendedPlan": {
    "checkInIntervalHours": 4,
    "actions": [
      "Run a grounding exercise (5-4-3-2-1)",
      "Reach out to a trusted contact"
    ]
  },
  "generatedAt": "2026-01-01T00:00:00.000Z",
  "disclaimer": "This recommendation is not a medical diagnosis. Contact a qualified professional for urgent or clinical support."
}
```

## Environment Variables

See `.env.example`.

- `NODE_ENV` (required): runtime environment (`development`, `test`, `production`)
- `PORT` (optional): API port (default `3000`)
- `REQUEST_BODY_LIMIT_BYTES` (optional): max JSON body size (default `16384`)
- `CORS_ORIGIN` (optional): allowed CORS origin (default `*`)

## Scripts

- `npm run dev` - start in watch mode
- `npm start` - start production server
- `npm run lint` - syntax checks for source and tests
- `npm test` - run Node.js test suite

## Docker

Build image:

```bash
docker build -t soulcare-api:local .
```

Run container:

```bash
docker run --rm -p 3000:3000 -e NODE_ENV=production soulcare-api:local
```

## Project Structure

- `src/index.js` - application entrypoint and graceful shutdown
- `src/server.js` - HTTP routes, request handling, response headers
- `src/supportPlan.js` - starter stress support recommendation logic
- `src/config.js` - environment parsing and validation
- `src/logger.js` - structured logging
- `tests/server.test.js` - API tests
- `.github/workflows/ci.yml` - CI test workflow
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
