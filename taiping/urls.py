from django.shortcuts import redirect
from django.urls import path

from . import views


index_redirect = lambda request: redirect("/courses/")

urlpatterns = [
    path('register/<int:course_id>/', views.RegisterView.as_view(), name="register"),
    path('courses/', views.CoursesView.as_view(), name="courses"),
    path('', index_redirect),
]
