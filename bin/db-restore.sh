#!/usr/bin/env bash
set -eu

readonly filename="${1:?}"

gunzip <"${filename}" \
  | docker compose exec --user postgres --no-tty db \
      psql -X postgres
