# Slice 1 Local Runbook

## Prerequisites

- Docker with Docker Compose v2.

No local Python, Node.js, or PostgreSQL installation is required.

## Configure

From the repository root:

```sh
cp infra/.env.example infra/.env
```

Set a random `AUTH_SECRET` of at least 32 characters.

For local HTTP keep:

```text
AUTH_COOKIE_SECURE=false
```

When the browser-facing application is exposed through an HTTPS tunnel, set it to `true`.

Set `DEV_ALLOWED_HOSTS` to the exact external tunnel hostname (comma-separated if more than one host is required). Do not use a wildcard host policy.

## Run the development stack

```sh
docker compose --env-file infra/.env -f infra/compose.yaml up --build
```

Open the web application at `http://localhost:5173`.

The API health endpoint is `http://localhost:8000/health`.

## Verify Slice 1

The verification script uses a dedicated Compose project and dedicated host ports, then removes its own volumes on exit:

```sh
./scripts/verify-slice1.sh
```

It performs:

1. backend and frontend image builds;
2. Alembic migration of the PostgreSQL test database;
3. backend unit/integration tests;
4. TypeScript/Vite production build;
5. API/web startup;
6. Playwright success and failure Slice 1 flows.

The verification project does not reuse or delete the normal development Compose volumes.

## Tunnel exposure

Expose the **web origin** only. The Vite proxy forwards `/api` to FastAPI.

The tunnel is transport only and is not an authentication or authorization boundary.

Before external exposure:

- use a non-default random `AUTH_SECRET`;
- set `AUTH_COOKIE_SECURE=true`;
- do not expose PostgreSQL directly.
