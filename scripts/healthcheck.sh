#!/usr/bin/env bash
# ============================================================================
# scripts/healthcheck.sh
# Manual health check script — run against any environment
#
# Usage:
#   ./scripts/healthcheck.sh dev
#   ./scripts/healthcheck.sh staging
#   ./scripts/healthcheck.sh prod
#   ./scripts/healthcheck.sh http://custom-host:8000
# ============================================================================

set -euo pipefail

ENV="${1:-dev}"

# Map environment names to hosts
case "$ENV" in
  dev)
    BACKEND_HOST="http://dev-backend.sapsecops.in:8000"
    FRONTEND_HOST="http://dev.sapsecops.in"
    ;;
  staging)
    BACKEND_HOST="http://staging-backend.sapsecops.in:8000"
    FRONTEND_HOST="http://staging.sapsecops.in"
    ;;
  prod)
    BACKEND_HOST="https://api.admin.sapsecops.in"
    FRONTEND_HOST="https://admin.sapsecops.in"
    ;;
  http*)
    # Custom URL passed directly
    BACKEND_HOST="$ENV"
    FRONTEND_HOST=""
    ;;
  *)
    echo "Usage: $0 [dev|staging|prod|http://custom-url]"
    exit 1
    ;;
esac

PASS=0
FAIL=0

check() {
  local label="$1"
  local url="$2"
  local expected_status="${3:-200}"

  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null || echo "000")

  if [ "$HTTP_STATUS" = "$expected_status" ]; then
    echo "  ✅  $label → $HTTP_STATUS"
    PASS=$((PASS + 1))
  else
    echo "  ❌  $label → $HTTP_STATUS (expected $expected_status)"
    FAIL=$((FAIL + 1))
  fi
}

echo ""
echo "══════════════════════════════════════════"
echo "  SapSecOps Health Check — ENV: $ENV"
echo "══════════════════════════════════════════"

echo ""
echo "Backend ($BACKEND_HOST):"
check "/health"        "$BACKEND_HOST/health"
check "/health/live"   "$BACKEND_HOST/health/live"
check "/health/ready"  "$BACKEND_HOST/health/ready"
check "API docs"       "$BACKEND_HOST/api/docs"

if [ -n "$FRONTEND_HOST" ]; then
  echo ""
  echo "Frontend ($FRONTEND_HOST):"
  check "Frontend home" "$FRONTEND_HOST"
fi

echo ""
echo "──────────────────────────────────────────"
echo "  Results: $PASS passed, $FAIL failed"
echo "──────────────────────────────────────────"

if [ "$FAIL" -gt 0 ]; then
  echo "  ⚠️  Health check FAILED — investigate before deploying further"
  exit 1
else
  echo "  🎉 All checks passed!"
  exit 0
fi
