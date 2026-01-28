from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import path, re_path, include

from . import views


urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),

    path('course/<int:course_id>/enrolled/<int:course_class_id>/', login_required(views.EnrollView.as_view()), {"enrolled": True}, name="enrolled"),
    path('course/<int:course_id>/enroll/<int:course_class_id>/', login_required(views.EnrollView.as_view()), name="enroll"),
    path('course/<int:course_id>/enroll/', login_required(views.EnrollView.as_view()), name="enroll"),

    path('course/new/', login_required(views.CourseEditView.as_view()), name="course_add"),
    path('course/<int:course_id>/edit/', login_required(views.CourseEditView.as_view()), name="course_edit"),

    path('course/<int:course_id>/', views.CourseView.as_view(), name="course"),
    path('course/', views.CourseView.as_view(), name="course_list"),

    path('create-account/created/', views.CreateAccountView.as_view(), {"created": True}, name="account_created"),
    path('create-account/instructor/', views.CreateAccountView.as_view(), {"user_type": "instructor"}, name="create_account"),
    path('create-account/', views.CreateAccountView.as_view(), name="create_account"),

    path('class/<int:course_class_id>/', views.CourseClassView.as_view(), name="course_class"),

    path('ics/<int:course_class_id>/', login_required(views.IcsView.as_view()), name="ics"),

    re_path(r'(?P<info_type>terms-and-conditions)/', views.InfoView.as_view(), name="terms_and_conditions"),
    re_path(r'(?P<info_type>indemnity-waiver)/', views.InfoView.as_view(), name="indemnity_waiver"),

    path('', views.IndexView.as_view(), name="index"),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
