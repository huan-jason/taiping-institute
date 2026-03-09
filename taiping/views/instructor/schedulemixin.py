from datetime import date, timedelta
from itertools import groupby
import operator
from typing import Any

from django.db.models import QuerySet

from taiping.models import Instructor, CourseClassSchedule


class ScheduleMixin:

    def schedule__add_date_events(self,
        dates: list[dict[str, Any]],
        instructor: Instructor,
    ) -> list[dict[str, Any]]:

        events: dict[date, list[CourseClassSchedule]] = self.schedule__get_instructor_events(
            dates=dates,
            instructor=instructor,
        )
        course_class_css_classes: dict[int, str] = self.schedule__get_course_class_css_classes(
            dates=dates,
            instructor=instructor,
        )

        for item in dates:
            item["events"] = events.get(item["date"], [])

            for event_item in item["events"]:
                event_item.css_class = course_class_css_classes[event_item.course_class_id]  # type: ignore

        return dates

    def schedule__get_calendar_dates(self, instructor: Instructor, month: date) -> list[dict[str, Any]]:
        first_of_the_month: date = month.replace(day=1)
        next_month: date = self.schedule__get_first_of_next_month(month)
        first_date: date = first_of_the_month - timedelta(days=first_of_the_month.weekday())

        dates: list[dict[str, Any]] = []
        date_: date = first_date

        while date_ < next_month:

            for i in range(7):
                dates.append({
                    "date": date_,
                    "events": [],
                })
                date_ = date_ + timedelta(days=1)

        return dates

    def schedule__get_course_class_css_classes(self,
        dates: list[dict[str, Any]],
        instructor: Instructor,
    ) -> dict[int, str]:

        queryset: QuerySet[CourseClassSchedule, Any] = (CourseClassSchedule.objects
            .filter(
                course_class__instructor=instructor,
                class_date__range=[dates[0]["date"], dates[-1]["date"]],
            )
            .distinct("course_class_id")
            .values_list("course_class_id", flat=True)
        )
        return {
            item: f"event--{i}"
            for i, item in enumerate(queryset, 1)
        }

    def schedule__get_first_of_next_month(self, date_: date) -> date:
        month_: int = date_.month + 1
        year_: int = date_.year

        if month_ == 13:
            month_ = 1
            year_ += 1

        return date_.replace(
            year=year_,
            month=month_,
            day=1,
        )

    def schedule__get_instructor_events(self,
        dates: list[dict[str, Any]],
        instructor: Instructor,
    ) -> dict[date, list[CourseClassSchedule]]:

        queryset: QuerySet[CourseClassSchedule] = (CourseClassSchedule.objects
            .filter(
                course_class__instructor=instructor,
                class_date__range=[dates[0]["date"], dates[-1]["date"]],
            )
            .select_related("course_class")
            .order_by("class_date", "class_time_start")
        )
        groups = groupby(queryset, key=operator.attrgetter("class_date"))
        return {
            group: list(data_iter)
            for group, data_iter in groups
        }
