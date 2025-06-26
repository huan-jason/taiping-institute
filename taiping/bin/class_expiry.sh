#!/usr/bin/env bash
set -eu

readonly SCRIPT_DIR="$(dirname "$(readlink -f $0)")"
readonly LOG_DIR="$SCRIPT_DIR/../../../logs"

mkdir -p $LOG_DIR

docker compose exec app ./manage.py class_expiry >>$LOG_DIR/class_expiry.log
