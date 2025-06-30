import calendar
from collections import defaultdict
from datetime import date, datetime, timedelta, time
from typing import Generator
from uuid import uuid4

from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from taiping.models import CourseClass, CourseClassSchedule


class ClassScheduleMixin:

    def get_calendar(self, calendar_month: date, course_class: CourseClass) -> list[dict]:

        if not course_class.start_date or not course_class.end_date:
            return []

        course_class_schedule_data: dict[date, list[CourseClassSchedule]] = (
            self.get_course_class_schedule_data(course_class)
        )
        month: int = calendar_month.month
        year: int = calendar_month.year
        dates: Generator[date, None, None] = self.get_dates(
            month=month,
            year=year,
            end_date=course_class.end_date,
        )
        data: list[dict] = []
#
        for item in dates:
            data.append({
                "date": item,
                "data": course_class_schedule_data.get(item),
            })

        return data

    def get_course_class_schedule_data(self, course_class: CourseClass) -> dict[date, list[CourseClassSchedule]]:
        qs: QuerySet[CourseClassSchedule] = (course_class
            .courseclassschedule_set  # type: ignore
            .order_by("class_time_start", "class_time_end")
        )
        data: defaultdict = defaultdict(list)

        for item in qs:
            data[item.class_date].append(item)

        return dict(data)

    def get_dates(self, end_date: date, month: int, year: int) -> Generator[date, None, None]:
        if month > end_date.month: return

        start_date: date = date(year, month, 1)
        weekday: int = start_date.isoweekday()
        calendar_date: date = start_date - timedelta(days=weekday % 7)
        columns: int = 7
        max_count: int = 35
        count: int = 0

        last_day: int = calendar.monthrange(year, month)[1]
        cal_end: date = date(year, month, last_day)

        while True:
            yield calendar_date
            count += 1

            if count >= max_count:
                break

            if calendar_date >= cal_end and count % columns == 0:
                break

            calendar_date = calendar_date + timedelta(days=1)

    def get_month_next(self, calendar_month: date, course_class: CourseClass) -> date | None:
        if not course_class.end_date:
            return None
        cal_date: date = calendar_month.replace(day=1)
        if cal_date >= course_class.end_date.replace(day=1):
            return None
        return cal_date + timedelta(days=31)

    def get_month_prev(self, calendar_month: date, course_class: CourseClass) -> date | None:
        if not course_class.start_date:
            return None
        cal_date: date = calendar_month.replace(day=1)
        if cal_date <= course_class.start_date.replace(day=1):
            return None
        return cal_date - timedelta(days=1)

    def get_post_data(self, request: HttpRequest) -> dict[str, dict]:
        data: defaultdict[str, dict] = defaultdict(dict)

        for key in request.POST:
            if "--" not in key: continue
            name, obj_id = key.rsplit("--", 1)
            data[obj_id][name] = request.POST[key]

        return dict(data)

    def htmx_add_schedule(self, request: HttpRequest) -> HttpResponse:
        item_id: str = str(uuid4())
        return render(request, "taiping/course/modal_class_schedule/add_schedule_item.html", locals())

    def htmx_delete_schedule(self, request: HttpRequest) -> HttpResponse:
        item_id: str = request.GET["id"]
        is_new_item: bool = len(item_id) > 10
        return render(request, "taiping/course/modal_class_schedule/delete_schedule_item.html", locals())

    def htmx_load_calendar(self, request: HttpRequest) -> HttpResponse:
        course_class: CourseClass = CourseClass.objects.get(id=int(request.GET["id"]))
        month: str | None = request.GET.get("month")
        calendar_month: date = (
            datetime.strptime(month, "%Y%m%d").date() if month else
            course_class.start_date
        )
        calendar: list[dict] = self.get_calendar(calendar_month, course_class)
        prev_month: date | None = self.get_month_prev(calendar_month, course_class)
        next_month: date | None = self.get_month_next(calendar_month, course_class)
        return render(request, "taiping/course/calendar.html", locals())

    def htmx_modal_class_schedule(self, request: HttpRequest) -> HttpResponse:
        class_date: date = datetime.strptime(request.GET["date"], "%Y%m%d").date()
        course_class_id: int = int(request.GET["course_class"])
        course_class_schedules: QuerySet[CourseClassSchedule] = (CourseClassSchedule.objects
            .filter(
                course_class_id=course_class_id,
                class_date=class_date,
            )
            .order_by(
                "class_time_start",
                "class_time_end",
            )
        )
        return render(request, "taiping/course/modal_class_schedule/modal_content.html", locals())

    def htmx_save(self, request: HttpRequest) -> HttpResponse:
        course_class_id: int = int(request.POST["course_class_id"])
        class_date: date = date(*[
            int(item) for item in request.POST["class_date"].split("-")
        ])
        post_data: dict[str, dict] = self.get_post_data(request)

        obj_ids: list[int] = [
            int(key) for key in post_data
            if "-" not in key
        ]
        course_class_schedules: dict[int, CourseClassSchedule] = (CourseClassSchedule.objects
            .filter(course_class_id=course_class_id)
            .in_bulk(obj_ids)
        )

        with transaction.atomic():

            for obj_id, data in post_data.items():
                course_class_schedule: CourseClassSchedule = (
                    CourseClassSchedule(
                        course_class_id=course_class_id,
                        class_date=class_date,
                    )
                    if "-" in obj_id else
                    course_class_schedules[int(obj_id)]
                )

                for field, value in data.items():
                    if "time" in field:
                        value = time(*[
                            int(item) for item in value.split(":", 2)[:2]
                        ])  # type: ignore

                    setattr(course_class_schedule, field, value)

                course_class_schedule.save()

        response: HttpResponse = render(request, "taiping/course/modal_class_schedule/save.html", locals())
        response["HX-Trigger"] = "load-calendar"
        return response
