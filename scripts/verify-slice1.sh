#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/infra/compose.yaml"

export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-star-wars-rp-slice1-verify}"
export AUTH_SECRET="${AUTH_SECRET:-slice1-verification-secret-not-for-external-use}"
export AUTH_COOKIE_SECURE=false
export POSTGRES_PORT="${POSTGRES_PORT:-55432}"
export API_PORT="${API_PORT:-58000}"
export WEB_PORT="${WEB_PORT:-55173}"

compose() {
  docker compose -f "$COMPOSE_FILE" "$@"
}

cleanup() {
  compose --profile test down -v --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

cleanup
compose build api web
compose up -d db

# The init script creates star_wars_rp_test on a fresh verification volume.
compose run --rm \
  -e TEST_DATABASE_URL=postgresql+psycopg://starwars:starwars@db:5432/star_wars_rp_test \
  api pytest -q

compose run --rm web npm run build

compose up -d api web

i=0
until curl -fsS "http://127.0.0.1:${API_PORT}/health" >/dev/null; do
  i=$((i + 1))
  if [ "$i" -ge 60 ]; then
    echo "API did not become healthy" >&2
    compose logs api
    exit 1
  fi
  sleep 1
done

i=0
until curl -fsS "http://127.0.0.1:${WEB_PORT}/" >/dev/null; do
  i=$((i + 1))
  if [ "$i" -ge 60 ]; then
    echo "Web app did not become healthy" >&2
    compose logs web
    exit 1
  fi
  sleep 1
done

compose --profile test run --rm e2e

echo "Slice 1 verification passed."
