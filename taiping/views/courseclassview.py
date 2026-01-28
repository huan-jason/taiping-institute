from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from taiping.models import CourseClass, Registration


class CourseClassView(View):

    def get(self, request: HttpRequest, course_class_id: int) -> HttpResponse:
        show_back_button: bool = True
        course_class: CourseClass = CourseClass.objects.get(id=course_class_id)
        registrations: QuerySet[Registration] = (course_class
            .registration_set  # type: ignore
            .order_by(
                "student__user__first_name",
                "student__user__last_name",
            )
        )
        return render(request, "taiping/class/index.html", locals())
