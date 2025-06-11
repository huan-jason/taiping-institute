from django.urls import path, include

from . import views


urlpatterns = [
    path('register/<int:course_id>/', views.RegisterView.as_view(), name="register"),
    path('register/', views.RegisterView.as_view(), name="register"),
    path("accounts/", include("django.contrib.auth.urls")),
    path('', views.IndexView.as_view(), name="course"),
]
