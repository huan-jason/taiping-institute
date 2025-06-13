from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View


class CreateAccountView(View):

    def get(self, request: HttpRequest, course_id: int | None = None) -> HttpResponse:
        return render(request, 'taiping/create_account/index.html')

    def post(self, request: HttpRequest, course_id: int | None = None) -> HttpResponse:
        raise NotImplementedError
