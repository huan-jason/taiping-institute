from django.urls import path, include
from django.shortcuts import redirect

from . import views


redirect_to_course_view = lambda request: redirect("course_list")


urlpatterns = [
    path('register/<int:course_id>/', views.RegisterView.as_view(), name="register"),
    path('register/', views.RegisterView.as_view(), name="register"),
    path("accounts/", include("django.contrib.auth.urls")),

    path('course/<int:course_id>/', views.CourseView.as_view(), name="course"),
    path('course/', views.CourseView.as_view(), name="course_list"),

    path('', redirect_to_course_view, name="index"),
]
