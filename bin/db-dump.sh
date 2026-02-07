#!/usr/bin/env bash
set -eu

get-filename(){
  if [[ ${1} ]]; then
    echo ${1}
    return 0
  fi
  echo tmp/"dbdump_$(date +%F_%R)".gz
}

set +u
readonly filename="${1:-$(get-filename ${1})}"
set -u

docker compose exec --user postgres db \
  pg_dump postgres | gzip -f >"${filename}"

echo "${filename}"
