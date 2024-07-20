from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from taiping.models import Course


class RegisterView(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        courses: QuerySet[Course] = Course.objects.order_by("sort_order", "name")
        return render(request, "taiping/register.html", locals())

    def post(self, request: HttpRequest) -> HttpResponse:

        if "description" in request.GET:
            course_obj: Course | None = Course.objects.filter(id=request.POST["course_id"] or 0).first()
            return render(request, "taiping/course_description.html", locals())

        raise NotImplementedError
