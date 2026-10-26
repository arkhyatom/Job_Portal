

from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("jobs/", views.job_list, name="job_list"),
    path("jobs/<int:pk>/", views.job_detail, name="job_detail"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/candidate/", views.register_candidate, name="register_candidate"),
    path("register/employer/", views.register_employer, name="register_employer"),

    # Candidate
    path("jobs/<int:pk>/apply/", views.apply, name="apply"),
    path("my-applications/", views.my_applications, name="my_applications"),

    # Employer
    path("employer/jobs/", views.employer_dashboard, name="employer_dashboard"),
    path("employer/jobs/new/", views.post_job, name="post_job"),
    path("employer/jobs/<int:pk>/applicants/", views.job_applicants, name="job_applicants"),
]
