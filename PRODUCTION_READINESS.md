# PRODUCTION_READINESS Audit Report

## Executive summary
This repository is **not production-ready**. It contains two partially overlapping backends (Node.js and FastAPI), inconsistent documentation, and incomplete CI/test coverage. Core quality checks pass for Node syntax/tests and Python lint, but Python tests fail in current setup, type-checking is absent, and release/deployment/security governance requirements are largely missing.

## Verified capabilities
- Node HTTP API exists with `/health` and `/v1/support-plan` endpoints (`/home/runner/work/soulcare-ai/soulcare-ai/src/server.js`).
- FastAPI API exists with `/health` and `/v1/support/check-in` endpoints (`/home/runner/work/soulcare-ai/soulcare-ai/app/main.py`, `/home/runner/work/soulcare-ai/soulcare-ai/app/api/routes/support.py`).
- Node test workflow is configured in CI (`/home/runner/work/soulcare-ai/soulcare-ai/.github/workflows/ci.yml`).
- Python linting and tests are scaffolded (`/home/runner/work/soulcare-ai/soulcare-ai/pyproject.toml`, `/home/runner/work/soulcare-ai/soulcare-ai/tests`).

## Validation checks run (with evidence)

### 1) Node dependency install
- **Command:** `cd /home/runner/work/soulcare-ai/soulcare-ai && npm ci --ignore-scripts`
- **Result:** PASS
- **Relevant output:** `up to date, audited 1 package ... found 0 vulnerabilities`
- **Files affected:** `/home/runner/work/soulcare-ai/soulcare-ai/package.json`, `/home/runner/work/soulcare-ai/soulcare-ai/package-lock.json`, `node_modules/`
- **Remaining risks:** No runtime npm dependencies means this does not validate real supply-chain posture for application dependencies.

### 2) Python dependency install
- **Command:** `cd /home/runner/work/soulcare-ai/soulcare-ai && python -m venv .venv && . .venv/bin/activate && pip install -e .[dev]`
- **Result:** PASS
- **Relevant output:** `Successfully installed ... fastapi ... uvicorn ... pytest ... ruff ... soulcare-ai-0.1.0`
- **Files affected:** `/home/runner/work/soulcare-ai/soulcare-ai/pyproject.toml`, `/home/runner/work/soulcare-ai/soulcare-ai/.venv/`, `/home/runner/work/soulcare-ai/soulcare-ai/soulcare_ai.egg-info/`
- **Remaining risks:** No Python lockfile; dependency resolution is non-reproducible across environments.

### 3) Node lint
- **Command:** `cd /home/runner/work/soulcare-ai/soulcare-ai && npm run lint`
- **Result:** PASS
- **Relevant output:** `node --check src/*.js tests/*.js`
- **Files affected:** `/home/runner/work/soulcare-ai/soulcare-ai/src/*.js`, `/home/runner/work/soulcare-ai/soulcare-ai/tests/*.js`
- **Remaining risks:** Syntax-only lint; no style/security/static-analysis coverage.

### 4) Node tests
- **Command:** `cd /home/runner/work/soulcare-ai/soulcare-ai && npm test`
- **Result:** PASS
- **Relevant output:** `# pass 2`, `# fail 0`
- **Files affected:** `/home/runner/work/soulcare-ai/soulcare-ai/tests/server.test.js`, `/home/runner/work/soulcare-ai/soulcare-ai/src/server.js`, `/home/runner/work/soulcare-ai/soulcare-ai/src/supportPlan.js`
- **Remaining risks:** Very low test depth; no negative/security/load/concurrency coverage.

### 5) Python lint
- **Command:** `cd /home/runner/work/soulcare-ai/soulcare-ai && . .venv/bin/activate && ruff check .`
- **Result:** PASS
- **Relevant output:** `All checks passed!`
- **Files affected:** Python files under `/home/runner/work/soulcare-ai/soulcare-ai/app/` and `/home/runner/work/soulcare-ai/soulcare-ai/tests/`
- **Remaining risks:** Lint pass does not validate runtime behavior.

### 6) Python tests
- **Command:** `cd /home/runner/work/soulcare-ai/soulcare-ai && . .venv/bin/activate && pytest`
- **Result:** FAIL
- **Relevant output:**
  - `ModuleNotFoundError: No module named 'app'`
  - `ERROR tests/test_health.py`
  - `ERROR tests/test_support.py`
- **Files affected:** `/home/runner/work/soulcare-ai/soulcare-ai/tests/test_health.py`, `/home/runner/work/soulcare-ai/soulcare-ai/tests/test_support.py`
- **Remaining risks:** Python API behavior is not validated in CI-like execution; release confidence is low.

### 7) Python build command attempt
- **Command:** `cd /home/runner/work/soulcare-ai/soulcare-ai && . .venv/bin/activate && python -m build`
- **Result:** FAIL
- **Relevant output:** `/home/runner/work/soulcare-ai/soulcare-ai/.venv/bin/python: No module named build`
- **Files affected:** N/A (command/tooling check)
- **Remaining risks:** No documented/working Python artifact build pipeline for releases.

### 8) Container build
- **Command:** `cd /home/runner/work/soulcare-ai/soulcare-ai && docker build -t soulcare-api:local .`
- **Result:** PASS
- **Relevant output:** `naming to docker.io/library/soulcare-api:local done`
- **Files affected:** `/home/runner/work/soulcare-ai/soulcare-ai/Dockerfile`, `/home/runner/work/soulcare-ai/soulcare-ai/app/`, `/home/runner/work/soulcare-ai/soulcare-ai/pyproject.toml`
- **Remaining risks:** Dockerfile contains an unused Node stage and only packages Python runtime, while repository includes Node API and Node CI path.

### 9) Type-check command availability check
- **Command:** searched repository for type-check tooling references (`typecheck|mypy|pyright|tsc`)
- **Result:** FAIL (no type-check command/tool configured)
- **Relevant output:** no type-check scripts/config found
- **Files affected:** `/home/runner/work/soulcare-ai/soulcare-ai/package.json`, `/home/runner/work/soulcare-ai/soulcare-ai/pyproject.toml`, `/home/runner/work/soulcare-ai/soulcare-ai/.github/workflows/ci.yml`
- **Remaining risks:** No static type validation for either Node or Python code paths.

## Failed checks
- Python tests fail due to import/module path issues.
- Python build command (`python -m build`) is unavailable.
- No type-checking command/tool is configured.

## Critical blockers
1. **Architectural ambiguity:** dual Node/FastAPI stacks are both present but inconsistently documented/tested/deployed.
2. **Broken Python test execution:** cannot validate FastAPI path in default command invocation.
3. **CI coverage gap:** CI only runs Node tests; Python quality gates are not enforced.
4. **No explicit production deployment pipeline/environment promotion strategy.**

## High-priority improvements
- Pick a primary runtime (Node or FastAPI) and remove/retire the other, or fully support both with separate CI/CD paths.
- Fix Python test import path/package structure so `pytest` passes reliably.
- Expand CI to include Python install/lint/test and a reproducible build check.
- Add explicit type-check stage (`mypy`/`pyright` for Python or equivalent for JS/TS if adopted).
- Resolve README contradictions and align docs with the actual supported runtime(s).
- Add dependency scanning and SBOM generation in CI.

## Medium-priority improvements
- Add structured production config profiles for local/staging/prod and strict env validation.
- Tighten CORS defaults (`*` is unsafe for production).
- Add API error schema standardization and request validation tests.
- Add health/readiness split endpoints and deployment probes.
- Add runbooks for incidents and operational ownership.

## Missing production requirements by domain

1. **Local development**
   - Missing single-source setup path (Node and Python guides conflict in `README.md`).
   - Missing consistent dev bootstrap automation.

2. **Staging deployment**
   - No staging environment config set, no staging workflow, no pre-prod promotion gate.

3. **Production deployment**
   - No deployment workflow, release tagging/versioning process, rollback procedure, or SLO gate.

4. **Database and migrations**
   - No database integration, schema, migration tool, or migration policy documented.

5. **Authentication and authorization**
   - No authn/authz layer (no API keys/OAuth/JWT/RBAC) and no endpoint access control strategy.

6. **Secrets management**
   - `.env` usage exists, but no secret manager integration, key rotation policy, or secret scanning gate in CI.

7. **Observability**
   - Minimal logs only; no metrics, tracing, alerting, dashboards, or log retention policy.

8. **Backup and recovery**
   - No backup policy, restore tests, RPO/RTO targets, or disaster-recovery documentation.

9. **Dependency and supply-chain security**
   - No automated dependency update strategy, SBOM, artifact signing, provenance, or vulnerability scan pipeline beyond ad-hoc npm audit output.

10. **Responsible AI and mental wellness privacy**
   - No documented data governance for sensitive wellness signals, consent model, retention/deletion policy, model risk controls, or escalation protocol for high-risk mental-health situations.

## Recommended next steps
1. Decide canonical runtime and remove unsupported path or operationalize both fully.
2. Make Python tests pass and enforce both runtime checks in CI.
3. Define environment matrix (local/staging/prod), deployment pipeline, and rollback controls.
4. Add security/observability baselines (auth, secrets management, metrics/tracing/alerts, dependency scanning).
5. Publish privacy and responsible-AI policy for mental wellness data handling before production exposure.
