# TD SYNNEX Product Matcher

A secure, internal-use mock-mode MVP for matching technical requirements to active, orderable, regionally eligible catalog products and exporting Excel quotes.

> **Important:** All bundled products, prices, SKUs, inventory, warehouses, and dates are clearly synthetic demonstration data. The live client contains no invented API contract and will remain disabled until official, account-specific TD SYNNEX documentation is supplied.

## Start with one command

```bash
docker compose up --build
```

Open <http://localhost:8080>. The API documentation is proxied at <http://localhost:8080/api/docs>.

## Repository structure

```text
backend/
  app/                 FastAPI API, client boundary, scoring, models, Excel export
  tests/               Automated acceptance tests
  Dockerfile
frontend/
  src/                 React/TypeScript single-page UI
  Dockerfile           Vite build served by nginx
docker-compose.yml
.env.example
```

## Local development

Requires Python 3.12 and Node.js 20+.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements-dev.txt
PYTHONPATH=backend uvicorn app.main:app --reload
```

In a second terminal:

```bash
cd frontend && npm install && npm run dev
```

When running Vite outside Docker, set its API proxy target to `http://localhost:8000` if needed. Production assets use nginx to proxy `/api` without exposing credentials.

## Matching safeguards

- Scores use the requested 50/15/15/10/5/5 weights and expose every component.
- Products under 70%, blocked lifecycle states, or non-orderable items are excluded.
- Mandatory failures appear only when exceptions are explicitly permitted and remain labelled as exceptions.
- Unknown lifecycle and unconfirmed regional eligibility are separated from recommendations.
- Missing specifications cap confidence and receive **Requires verification**; missing price is never estimated.
- Export values are formula-injection sanitized. Only normalized product data is exported.

## Live integration

Copy `.env.example` to `.env` only when configuring an environment. Backend-only credential variables are deliberately absent from frontend configuration. `LiveTdSynnexClient` documents the integration seam but does not assume endpoints, authentication, response fields, regional codes, lifecycle semantics, rate-limit behavior, or inventory/pricing contracts. Complete it only from official documentation, including explicit timeout and 429 retry handling appropriate to that contract.

SQLite is the default. SQLAlchemy and the PostgreSQL driver are installed so `DATABASE_URL` can use PostgreSQL in production when persistence is introduced; this stateless MVP queries the configured distributor client directly.

## Tests

```bash
PYTHONPATH=backend pytest backend/tests -q
cd frontend && npm run build
```
