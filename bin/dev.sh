#!/usr/bin/env bash
# Run Django dev server
set -u

port=8000
sleep=2

while getopts 'p:' opt; do
  case $opt in
    p) port=$OPTARG;;
  esac
done
shift $((OPTIND-1))


while true; do

  docker compose exec app \
    python ./manage.py runserver 0.0.0.0:${port:-''}

  echo -e "\nSleep ${sleep}s...\n"
  sleep ${sleep}

done
