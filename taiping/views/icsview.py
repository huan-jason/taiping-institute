from datetime import datetime
from io import StringIO
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.views import View

from ical.calendar import Calendar  # type: ignore
from ical.calendar_stream import IcsCalendarStream  # type: ignore
from ical.event import Event  # type: ignore

from taiping.models import CourseClass, CourseClassSchedule


class IcsView(View):

    def get(self, request: HttpRequest, course_class_id: int) -> HttpResponse:
        course_class: CourseClass = (CourseClass.objects
            .select_related("course")
            .get(id=course_class_id)
        )
        course_class_schedules: QuerySet[CourseClassSchedule] = (course_class
            .courseclassschedule_set  # type: ignore
            .filter(class_date__range=[
                course_class.start_date,
                course_class.end_date
            ])
            .order_by(
                "class_date",
                "class_time_start",
                "class_time_end",
            )
        )
        calendar: Calendar = self.get_calendar(course_class, course_class_schedules)
        return self.get_response(calendar, course_class)

    def get_calendar(self, course_class: CourseClass, course_class_schedules: QuerySet[CourseClassSchedule]) -> Calendar:
        calendar: Calendar = Calendar()

        for item in course_class_schedules:
            calendar.events.append(
                Event(
                    summary=course_class.course.full_name,
                    dtstart=datetime.combine(item.class_date, item.class_time_start),
                    dtend=datetime.combine(item.class_date, item.class_time_end),
                )
            )

        return calendar

    def get_response(self, calendar: Calendar, course_class: CourseClass) -> HttpResponse:
        ics_file: StringIO = StringIO()
        ics_file.write(IcsCalendarStream.calendar_to_ics(calendar))
        ics_file.seek(0)

        return HttpResponse(
            ics_file.read(),
            content_type="text/calendar",
            headers={
                "Content-Disposition": f"attachment; filename={course_class.course.name}.ics",
            },
        )
