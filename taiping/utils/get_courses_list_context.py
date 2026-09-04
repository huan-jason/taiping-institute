# from datetime import datetime
from typing import Any

from django.db.models import Q, QuerySet, OuterRef, Exists
from django.http import HttpRequest

from taiping.constants import CourseStatusChoices
from taiping.models import Course, CourseClass, Facility, Instructor


def _get_courses_queryset(
    request: HttpRequest,
    filters: dict[str, str],
    status: CourseStatusChoices | None = None,
) -> QuerySet[Course]:

    queryset: QuerySet[Course] = (Course.objects
        .order_by("sort_order", "name")
    )
    if status:
        queryset = queryset.filter(status=CourseStatusChoices.PUBLISHED)

    if (instructor := filters.get("filter_instructor")):
        subquery_instructor: QuerySet[CourseClass] = CourseClass.objects.filter(
            course_id=OuterRef('id'),
            instructor_id=int(instructor),
            status=CourseStatusChoices.PUBLISHED,
        )
        queryset = queryset.filter(
            Q(instructor_id=int(instructor))
            | Q(Exists(subquery_instructor))
        )

    if (facility := filters.get("filter_facility")):
        subquery_facility: QuerySet[CourseClass] = CourseClass.objects.filter(
            course_id=OuterRef('id'),
            facility_id=int(facility),
            status=CourseStatusChoices.PUBLISHED,
        )
        queryset = queryset.filter(
            Q(facility_id=int(facility))
            | Q(Exists(subquery_facility))
        )

    if (course_group := filters.get("filter_course_group")):
        queryset = queryset.filter(course_group_id=int(course_group))

    # if (filter_month := filters.get("filter_month")):
    #     filter_datetime: datetime = datetime.strptime(filter_month, "%Y-%m")
    #     year: int = filter_datetime.year
    #     month: int = filter_datetime.month

    #     q_start_date: Q = Q(start_date__year=year, start_date__month=month)
    #     q_end_date: Q = Q(end_date__year=year, end_date__month=month)

    #     subquery_date: QuerySet[CourseClass] = CourseClass.objects.filter(
    #         q_start_date | q_end_date,
    #         course_id=OuterRef('id'),
    #         status=CourseStatusChoices.PUBLISHED,
    #     )
    #     queryset = queryset.filter(Exists(subquery_date))

    return queryset


def get_courses_list_context(
    request: HttpRequest,
    use_session_filters: bool = False,
    status: CourseStatusChoices | None = None,
) -> dict[str, Any]:

    query_filters: dict[str, Any] = (
        request.session.get("course_filters") or {}
        if use_session_filters else
        {
            key: request.GET[key]
            for key in request.GET
            if key.startswith("filter_")
        }
    )
    filters: dict = {
        key: int(val) if val and key != "filter_month" else val
        for key, val in query_filters.items()
    }
    has_filters: bool = any(filters.values())
    courses: QuerySet[Course] = _get_courses_queryset(
        request=request,
        filters=filters,
        status=status,
    )
    course_groups: QuerySet[Course] = (Course.objects
        .select_related("course_group")
        .distinct("course_group__name")
        .order_by("course_group__name")
    )
    facilities: QuerySet[Facility] = Facility.objects.order_by("name")
    instructors: QuerySet[Instructor] = Instructor.objects.order_by(
        "user__first_name",
        "user__last_name",
    )
    return {
        "filters": filters,
        "has_filters": has_filters,
        "courses": courses,
        "course_groups": course_groups,
        "facilities": facilities,
        "instructors": instructors,
    }
