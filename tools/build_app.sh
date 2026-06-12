#!/usr/bin/env bash
# Databricks Apps build entrypoint (root package.json "build" script).
#
# Builds the client app and the docs site in parallel, so total build time is
# bounded by the slower of the two instead of their sum. The spec-coverage
# JSON the docs import at compile time is generated best-effort: the analyzer
# needs uv and playwright, which the Apps Node build container may not
# provide, and the docs must still ship (rendering "no coverage data")
# rather than fail the whole build.
set -uo pipefail

export NPM_CONFIG_REGISTRY="${NPM_CONFIG_REGISTRY:-https://registry.npmjs.org/}"

log() { printf '[build] %s\n' "$*"; }

build_client() {
  npm -C client install && npm -C client run build
}

generate_coverage() {
  mkdir -p docs/static
  # Full-fidelity coverage needs uv (pytest marker collection) and the
  # playwright CLI; without them the analyzer's fallback scanner badly
  # underreports. In that case prefer the committed snapshot (kept in sync
  # by `just spec-coverage`, like SPEC_COVERAGE_MAP.md) over degraded data.
  if command -v uv >/dev/null 2>&1 \
      && python3 tools/spec_coverage_analyzer.py --json > /tmp/spec-coverage-fresh.json 2>/tmp/spec-coverage-analyzer.err \
      && [ -s /tmp/spec-coverage-fresh.json ]; then
    cp /tmp/spec-coverage-fresh.json docs/static/spec-coverage.json
    log "spec coverage data regenerated (full fidelity)"
  elif [ -s docs/static/spec-coverage.json ]; then
    log "uv unavailable; using committed spec coverage snapshot"
  else
    log "WARNING: no analyzer and no committed snapshot; docs will render without coverage data"
    printf '{"specs": {}}\n' > docs/static/spec-coverage.json
  fi
}

build_docs() {
  npm -C docs install && generate_coverage && npm -C docs run build
}

build_client > >(sed 's/^/[client] /') 2>&1 &
CLIENT_PID=$!
build_docs > >(sed 's/^/[docs] /') 2>&1 &
DOCS_PID=$!

CLIENT_RC=0
DOCS_RC=0
wait "$CLIENT_PID" || CLIENT_RC=$?
wait "$DOCS_PID" || DOCS_RC=$?

if [ "$CLIENT_RC" -eq 0 ]; then log "client build OK"; else log "client build FAILED (exit $CLIENT_RC)"; fi
if [ "$DOCS_RC" -eq 0 ]; then log "docs build OK"; else log "docs build FAILED (exit $DOCS_RC)"; fi

if [ "$CLIENT_RC" -ne 0 ] || [ "$DOCS_RC" -ne 0 ]; then
  exit 1
fi
