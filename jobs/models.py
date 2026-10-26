from django.db import models 
from django.contrib.auth.models   import User

# Create your models here.
class CandidateProfile(models.Model):
    name=models.CharField(max_length=200)
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    age=models.PositiveIntegerField()
    phone=models.CharField(max_length=15)
    resume=models.FileField(blank=True, upload_to='resumes/')
    created_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
class EmployerProfile(models.Model):
    company_name=models.CharField(max_length=200)
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    phone=models.CharField(max_length=15)
    location=models.CharField(max_length=100)
    description=models.TextField(blank=True)
    website=models.URLField(blank=True)
    logo=models.ImageField(blank=True, upload_to='logos/')
    date=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.company_name
    
    
    
class Jobtype(models.TextChoices):
    Fulltime="f", "Full-time"
    Parttime="p", "Part-time"
    Remote="r", "Remote"
        
        
class Job(models.Model):
    employer=models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name="jobs")
    job_title=models.CharField(max_length=200)
    description=models.TextField()
    salary=models.PositiveIntegerField(null=True, blank=True, help_text="Yearly salary in rupees")
    location=models.CharField(max_length=100)
    job_type=models.CharField(max_length=20, choices=Jobtype.choices, default=Jobtype.Fulltime)
    created_at=models.DateTimeField(auto_now_add=True)
    deadline=models.DateField(null=True,blank=True)
    is_active=models.BooleanField(default=True)
        
    def __str__(self):
        return self.job_title
    
    
    
class ApplicationStatus(models.TextChoices):
    Applied="a", "Applied"
    Shortlisted="s", "Shortlisted"
    Rejected="r", "Rejected"
    
    
class Application(models.Model):
    job=models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    candidate=models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name="applications")
    status=models.CharField(max_length=20, choices=ApplicationStatus.choices, default=ApplicationStatus.Applied)
    cover_letter=models.TextField(blank=True)
    applied_at=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together=('candidate', 'job')
        
    
    def __str__(self):
        return f"{self.candidate.name} - {self.job.job_title}"
    
    