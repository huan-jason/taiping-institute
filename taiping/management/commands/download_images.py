from pathlib import Path
from typing import Any, cast

import requests

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from django.db.models import QuerySet

from taiping.models import Course


class Command(BaseCommand):

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--all", action="store_true", help="include previously processed courses")
        parser.add_argument("course_ids", nargs="*", metavar="Course ID")

    def handle(self, *args: Any, **options: Any) -> None:
        static_dir: Path = settings.STATIC_ROOT
        base_dir: Path = static_dir.parent / "taiping/static/course_images"
        base_dir.mkdir(parents=True, exist_ok=True)
        headers: dict[str, str] = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
        }

        queryset: QuerySet = Course.objects.filter(image__startswith="http://")
        if options["course_ids"]:
            queryset = queryset.filter(id__in=options["course_ids"])

        if not options["all"]:
            queryset = queryset.filter(static_url__isnull=True)

        for obj in queryset:
            print(f"Downloading {obj.image}")
            url: str = cast(Any, obj.image)
            response: requests.Response = requests.get(url, headers=headers)
            ext: str = url.rsplit(".")[-1]
            path: Path = base_dir / f"{obj.id}.{ext}"

            with open(path, "wb") as fp:
                fp.write(response.content)

            obj.static_url = str(path).removeprefix("/app/taiping")
            obj.save()

