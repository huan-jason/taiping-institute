from pathlib import Path
from typing import Any

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from taiping.models import Course


class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any) -> None:

        with transaction.atomic():

            for item in Course.objects.all():
                self.small_image(item)

    def small_image(self, course: Course) -> None:
        image_name: str = course.image.file.name
        small_image_name: str = image_name.replace("/course/", "/course/resized/")

        try: small_image = open(small_image_name, "rb")
        except FileNotFoundError: return None

        file_name: str = small_image_name.rsplit("/", 1)[-1]

        if not course.small_image:
            course.small_image.save(file_name, File(small_image))
            Path(small_image_name).unlink()
            self.stderr.write(small_image_name)
