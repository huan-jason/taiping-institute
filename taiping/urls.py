from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.shortcuts import redirect

from . import views


redirect_to_course_view = lambda request: redirect("course_list")


urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),

    path('course/<int:course_id>/enroll/<int:course_class_id>/', login_required(views.EnrollView.as_view()), name="enroll"),
    path('course/<int:course_id>/enroll/', login_required(views.EnrollView.as_view()), name="enroll"),
    path('course/<int:course_id>/', views.CourseView.as_view(), name="course"),
    path('course/', views.CourseView.as_view(), name="course_list"),

    path('create-account/instructor/', views.CreateAccountView.as_view(), { "user_type": "instructor" }, name="create_account"),
    path('create-account/', views.CreateAccountView.as_view(), name="create_account"),

    path('', redirect_to_course_view, name="index"),
]
