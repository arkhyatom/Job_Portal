from django.shortcuts import render
from .models import Job


from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (ApplicationForm, CandidateRegisterForm,
EmployerRegisterForm, JobForm)
from .models import (Application, ApplicationStatus, CandidateProfile,
EmployerProfile, Job, Jobtype)


# ---------- role check (Candidate മാത്രം / Employer മാത്രം) ----------
def candidate_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, "candidateprofile"):
            messages.error(request, "This page is only for job seekers.")
            return redirect("home")
        return view_func(request, *args, **kwargs)
    return wrapper


def employer_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, "employerprofile"):
            messages.error(request, "This page is only for employers.")
            return redirect("home")
        return view_func(request, *args, **kwargs)
    return wrapper


def home(request):
    active_jobs = Job.objects.filter(is_active=True)
    context = {
        "latest_jobs": active_jobs.select_related("employer").order_by("-created_at")[:4],
        "job_count": active_jobs.count(),
        "company_count": EmployerProfile.objects.count(),
        "candidate_count": CandidateProfile.objects.count(),
    }
    return render(request, "home.html", context)


def job_list(request):
    jobs = Job.objects.filter(is_active=True).select_related("employer")

    q = request.GET.get("q", "").strip()
    location = request.GET.get("location", "").strip()
    job_type = request.GET.get("job_type", "")

    if q:
        jobs = jobs.filter(Q(job_title__icontains=q) | Q(employer__company_name__icontains=q))
    if location:
        jobs = jobs.filter(location__icontains=location)
    if job_type:
        jobs = jobs.filter(job_type=job_type)

    context = {
        "jobs": jobs.order_by("-created_at"),
        "job_types": Jobtype.choices,
        "q": q,
        "location": location,
        "selected_type": job_type,
    }
    return render(request, "job_list.html", context)


def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk, is_active=True)
    candidate = getattr(request.user, "candidateprofile", None)
    already_applied = bool(candidate) and Application.objects.filter(job=job, candidate=candidate).exists()
    expired = bool(job.deadline and job.deadline < timezone.localdate())
    return render(request, "job_detail.html", {
        "job": job,
        "already_applied": already_applied,
        "expired": expired,
    })


def register_candidate(request):
    form = CandidateRegisterForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Account created. Welcome!")
        return redirect("job_list")
    return render(request, "register.html", {"form": form, "title": "Job seeker sign up"})


def register_employer(request):
    form = EmployerRegisterForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Company account created. You can post a job now.")
        return redirect("employer_dashboard")
    return render(request, "register.html", {"form": form, "title": "Employer sign up"})


# ---------- Candidate ----------
@candidate_required
def apply(request, pk):
    job = get_object_or_404(Job, pk=pk, is_active=True)
    candidate = request.user.candidateprofile

    if Application.objects.filter(job=job, candidate=candidate).exists():
        messages.info(request, "You have already applied for this job.")
        return redirect("my_applications")
    if job.deadline and job.deadline < timezone.localdate():
        messages.error(request, "The deadline for this job has passed.")
        return redirect("job_detail", pk=job.pk)

    form = ApplicationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        application = form.save(commit=False)
        application.job = job
        application.candidate = candidate
        application.save()
        messages.success(request, "Application sent.")
        return redirect("my_applications")
    return render(request, "apply.html", {"form": form, "job": job})


@candidate_required
def my_applications(request):
    applications = (request.user.candidateprofile.applications
                    .select_related("job__employer")
                    .order_by("-applied_at"))
    return render(request, "my_applications.html", {"applications": applications})


# ---------- Employer ----------
@employer_required
def employer_dashboard(request):
    jobs = (request.user.employerprofile.jobs
            .annotate(app_count=Count("applications"))
            .order_by("-created_at"))
    return render(request, "employer_dashboard.html", {"jobs": jobs})


@employer_required
def post_job(request):
    form = JobForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        job = form.save(commit=False)
        job.employer = request.user.employerprofile
        job.save()
        messages.success(request, "Job posted.")
        return redirect("employer_dashboard")
    return render(request, "post_job.html", {"form": form})


@employer_required
def job_applicants(request, pk):
    job = get_object_or_404(Job, pk=pk, employer=request.user.employerprofile)

    if request.method == "POST":
        application = get_object_or_404(Application, pk=request.POST.get("application_id"), job=job)
        new_status = request.POST.get("status")
        if new_status in ApplicationStatus.values:
            application.status = new_status
            application.save()
            messages.success(request, "Status updated.")
        return redirect("job_applicants", pk=job.pk)

    applications = job.applications.select_related("candidate").order_by("-applied_at")
    return render(request, "job_applicants.html", {
        "job": job,
        "applications": applications,
        "statuses": ApplicationStatus.choices,
    })
