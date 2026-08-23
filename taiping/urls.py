from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import path, re_path, include

from . import views


urlpatterns_course = [
    path('new/', login_required(views.CourseEditView.as_view()), name="course_add"),

    path('<int:course_id>/enrolled/<int:course_class_id>/', login_required(views.EnrollView.as_view()), {"enrolled": True}, name="enrolled"),
    path('<int:course_id>/enroll/<int:course_class_id>/', login_required(views.EnrollView.as_view()), name="enroll"),
    path('<int:course_id>/enroll/', login_required(views.EnrollView.as_view()), name="enroll"),

    path('<int:course_id>/edit/', login_required(views.CourseEditView.as_view()), name="course_edit"),
    path('<int:course_id>/', views.CourseView.as_view(), name="course"),

    path('', views.CourseView.as_view(), name="course_list"),
]


urlpatterns_create_account = [
    path('created/', views.CreateAccountView.as_view(), {"created": True}, name="account_created"),
    path('instructor/', views.CreateAccountView.as_view(), {"user_type": "instructor"}, name="create_account"),
    path('', views.CreateAccountView.as_view(), name="create_account"),
]


urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),

    path("course/", include(urlpatterns_course)),
    path("create-account/", include(urlpatterns_create_account)),

    path("instructor/", views.InstructorView.as_view(), name="instructor"),
    path("student/", views.StudentView.as_view(), name="student"),

    path('class/<int:course_class_id>/', views.CourseClassView.as_view(), name="course_class"),
    path('ics/<int:course_class_id>/', login_required(views.IcsView.as_view()), name="ics"),

    re_path(r'(?P<info_type>terms-and-conditions)/', views.InfoView.as_view(), name="terms_and_conditions"),
    re_path(r'(?P<info_type>indemnity-waiver)/', views.InfoView.as_view(), name="indemnity_waiver"),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path('', views.IndexView.as_view(), name="index"),
]
