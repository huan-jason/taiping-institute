#!/usr/bin/env bash
set -eu

readonly SCRIPT_DIR="$(dirname "$(readlink -f $0)")"
readonly PROJECT="$(basename ${SCRIPT_DIR%/bin})"

readonly HOST=${1:?}

echo -e HOST: "\e[33m" $HOST "\e[0m"

ssh $HOST "
  cd $PROJECT;

  echo -e \"\e[32m\"Applying changes...\"\e[0m\"
  git pull;

  echo -e \"\e[32m\"Restarting app...\"\e[0m\"
  docker compose restart app;

  echo -e \"\e[32m\"Applying DB migrations...\"\e[0m\"
  docker compose exec -t app ./manage.py migrate;
"
