from datetime import date, timedelta
from typing import Any
from django.utils import timezone
from taiping.models import Instructor


class ScheduleMixin:

    def schedule__get_calendar_dates(self, instructor: Instructor) -> list[dict[str, Any]]:
        today: date = timezone.now().date()
        first_of_the_month: date = today.replace(day=1)
        next_month: date = self.schedule__get_first_of_next_month(today)
        first_date: date = first_of_the_month - timedelta(days=first_of_the_month.weekday())

        dates: list[dict[str, Any]] = []
        date_: date = first_date

        while date_ < next_month:

            for i in range(7):
                dates.append({
                    "date": date_,
                    "events": [], # zzz
                })
                date_ = date_ + timedelta(days=1)

        return dates

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
