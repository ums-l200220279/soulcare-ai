# SoulCare Production Readiness Baseline

## 1) Baseline and scope lock

- **Canonical runtime:** FastAPI (`app/`) on Python 3.11
- **Deployment shape:** Single deployable API service
- **Environments:** local, staging, production
- **Service objectives (initial targets):**
  - Availability: 99.9% monthly
  - p95 latency: < 300ms for `/health`, < 750ms for `/v1/support/check-in`
  - Error budget: 43m 49s downtime/month at 99.9%
  - Data retention: 30 days by default (configurable)
  - Incident response: acknowledge within 15 minutes (staging/prod)

## 2) Architecture consolidation

- FastAPI is the production code path and authoritative API contract.
- Endpoint surface is versioned under `/v1/support`.
- Legacy Node starter remains non-production reference only and is excluded from deployment targets.

## 3) Configuration and secrets hardening

- All runtime controls are environment-configurable through `SOULCARE_*`.
- Staging/production reject wildcard CORS.
- Request size, rate limit, and idempotency retention are enforced via validated settings.
- Secret policy:
  - CI/build secrets in GitHub Actions secrets
  - Runtime secrets in environment-integrated secret manager
  - Rotation cadence every 90 days or emergency rotation on incident
  - Least-privilege access by environment and role

## 4) API quality and safety controls

- Standardized error envelope with request ID and stable error codes.
- Request-size protection and per-client/path rate limiting.
- Idempotency handling via `Idempotency-Key`.
- Audit-safe request logs (method/path/status/duration/request_id/client_ip) without raw body payloads.
- Crisis-language safety escalation path for self-harm indicators.

## 5) Test and verification baseline

- Python test import reliability via `tests/conftest.py`.
- Expanded tests include:
  - validation error contract
  - readiness endpoint
  - security headers and payload limits
  - idempotency behavior
  - rate-limit enforcement
  - safety escalation behavior
- Container smoke checks run in CI.

## 6) CI/CD production gates

- CI gates:
  - lint (`ruff check .`)
  - tests (`pytest`)
  - build (`python -m build`)
  - dependency vulnerability scan (`pip-audit`)
  - secret scan (`gitleaks`)
  - container build + `/health` smoke test
- Required branch protections (repository setting):
  - required status checks
  - required PR review before merge
  - restricted direct pushes to protected branches

## 7) Supply-chain and release integrity

- Dependency pinning in `pyproject.toml`.
- Reproducible artifact build in CI.
- SBOM generated for tagged releases and uploaded as release artifact.
- Monthly dependency review and risk triage.

## 8) Observability and operations

- `/health` and `/ready` probes available for platform checks.
- Structured request logging implemented for baseline telemetry.
- Ops runbook requirements:
  - incident severity model
  - escalation tree
  - rollback checklist
  - postmortem template with action tracking

## 9) Data governance and compliance readiness

- Data classification: wellness interaction metadata is sensitive application data.
- Logging policy: redact or avoid personal free-text signal bodies in operational logs.
- Retention/deletion: default 30-day retention with environment override.
- Access control: least-privilege by environment and operational role.
- Quarterly privacy/security control review.

## 10) Go-live readiness review checklist

- [ ] Production environment config reviewed and approved
- [ ] CI gates green on release candidate
- [ ] Security review completed and critical findings resolved
- [ ] Incident runbook validated in staging drill
- [ ] Rollback drill completed successfully
- [ ] Observability dashboards and alerts validated
- [ ] Data retention and deletion controls verified
- [ ] Formal sign-off from engineering + security + operations
