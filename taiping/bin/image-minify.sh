#!/usr/bin/env bash
readonly IMAGE_HEIGHT=300
readonly SCRIPT_DIR="$(dirname "$(readlink -f $0)")"
readonly APP_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd $APP_DIR/media/course || exit 1

for item in *; do
    [[ -d "$item" ]] && continue
    [[ -e "resized/$item" ]] && continue
    echo $item
    mkdir -p resized
    convert "$item" -resize x${IMAGE_HEIGHT} "resized/$item"
done

docker compose exec app python ./manage.py small_image

for item in resized/*; do
    echo >$item
done
