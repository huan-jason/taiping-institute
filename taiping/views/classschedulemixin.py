from collections import defaultdict
from datetime import date, timedelta
from typing import Generator
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from taiping.models import CourseClass, CourseClassSchedule


class ClassScheduleMixin:

    def get_class_schedule(self, course_class: CourseClass) -> list[dict]:

        if not course_class.start_date or not course_class.end_date:
            return []

        course_class_schedule_data: dict[date, list[CourseClassSchedule]] = (
            self.get_course_class_schedule_data(course_class)
        )
        month: int = course_class.start_date.month
        year: int = course_class.start_date.year
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
            .all()
        )
        data: defaultdict = defaultdict(list)

        for item in qs:
            data[item.class_date].append(item)

        return dict(data)

    def get_dates(self, end_date: date, month: int, year: int) -> Generator[date, None, None]:
        if month > end_date.month: return

        start_date: date = date(year, month, 1)
        calendar_date: date = start_date - timedelta(days=start_date.isoweekday())
        columns: int = 7
        max_count: int = 35
        count: int = 0

        while True:
            yield calendar_date
            count += 1

            if count >= max_count:
                break

            if calendar_date >= end_date and count % columns == 0:
                break

            calendar_date = calendar_date + timedelta(days=1)

    def get_month_next(self, calendar_month: date, course_class: CourseClass) -> date | None:
        if not course_class.end_date:
            return None
        cal_date: date = course_class.end_date.replace(day=1)
        if cal_date == calendar_month.replace(day=1):
            return None
        return cal_date + timedelta(days=31)

    def get_month_prev(self, calendar_month: date, course_class: CourseClass) -> date | None:
        if not course_class.start_date:
            return None
        cal_date: date = course_class.start_date.replace(day=1)
        if cal_date == calendar_month.replace(day=1):
            return None
        return cal_date - timedelta(days=1)

    def htmx_class_schedule(self, request: HttpRequest) -> HttpResponse:
        course_class: CourseClass = CourseClass.objects.get(id=int(request.GET["id"]))
        class_schedule: list[dict] = self.get_class_schedule(course_class)
        calendar_month: date = course_class.start_date
        prev_month: date | None = self.get_month_prev(calendar_month, course_class)
        next_month: date | None = self.get_month_next(calendar_month, course_class)
        return render(request, "taiping/course/schedule.html", locals())
