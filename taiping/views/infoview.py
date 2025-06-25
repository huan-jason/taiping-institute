from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from taiping.models import AppData


class InfoView(View):

    def get(self, request: HttpRequest, info_type: str) -> HttpResponse:

        info_type = info_type.replace("-", "_")
        app_data: AppData = AppData.objects.get(name=info_type)
        return render(request, "taiping/info/index.html", locals())
