from django.shortcuts import redirect
from django.urls import path

from . import views


redirect_to_register = lambda request: redirect("/register/")

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name="register"),
    path('', redirect_to_register),
]
