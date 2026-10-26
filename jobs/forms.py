from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Application, CandidateProfile, EmployerProfile, Job


class CandidateRegisterForm(UserCreationForm):
    name = forms.CharField(max_length=200, label="Full name")
    age = forms.IntegerField(min_value=16, max_value=80)
    phone = forms.CharField(max_length=15)
    resume = forms.FileField(required=False)

    def save(self, commit=True):
        user = super().save()
        CandidateProfile.objects.create(
            user=user,
            name=self.cleaned_data["name"],
            age=self.cleaned_data["age"],
            phone=self.cleaned_data["phone"],
            resume=self.cleaned_data.get("resume") or "",
        )
        return user


class EmployerRegisterForm(UserCreationForm):
    company_name = forms.CharField(max_length=200)
    phone = forms.CharField(max_length=15)
    location = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)
    website = forms.URLField(required=False)
    logo = forms.ImageField(required=False)

    def save(self, commit=True):
        user = super().save()
        EmployerProfile.objects.create(
            user=user,
            company_name=self.cleaned_data["company_name"],
            phone=self.cleaned_data["phone"],
            location=self.cleaned_data["location"],
            description=self.cleaned_data.get("description", ""),
            website=self.cleaned_data.get("website", ""),
            logo=self.cleaned_data.get("logo") or "",
        )
        return user


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["job_title", "description", "salary", "location", "job_type", "deadline"]
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 6}),
        }


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["cover_letter"]
        widgets = {"cover_letter": forms.Textarea(attrs={"rows": 6})}
