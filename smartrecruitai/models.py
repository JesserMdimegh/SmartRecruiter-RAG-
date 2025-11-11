"""
SmartRecruitAI Models
Core data models for CV, Job Offers, Matching, and Analytics
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class TimestampedModel(models.Model):
    """Abstract base model with timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class Recruiter(TimestampedModel):
    """Recruiter user profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recruiter_profile')
    company_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.company_name}"


class Candidate(TimestampedModel):
    """Candidate information extracted from CV"""
    full_name = models.CharField(max_length=200, blank=True, help_text="Will be extracted from CV")
    email = models.EmailField(blank=True, help_text="Will be extracted from CV")
    phone_number = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=200, blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    
    # Extracted skills and experiences
    technical_skills = models.JSONField(default=list, help_text="Technical skills extracted from CV")
    soft_skills = models.JSONField(default=list, help_text="Soft skills extracted from CV")
    languages = models.JSONField(default=list, help_text="Languages and proficiency levels")
    certifications = models.JSONField(default=list, help_text="Certifications and credentials")
    
    # Experience and Education
    total_experience_years = models.FloatField(default=0.0)
    education_level = models.CharField(max_length=100, blank=True)
    current_position = models.CharField(max_length=200, blank=True)
    
    # Additional metadata
    status = models.CharField(max_length=50, default='active', choices=[
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('hired', 'Hired'),
    ])
    availability = models.CharField(max_length=50, default='immediate', choices=[
        ('immediate', 'Immediate'),
        ('2 weeks', '2 weeks notice'),
        ('1 month', '1 month notice'),
        ('3 months', '3+ months'),
    ])
    
    # AI Extracted Data
    cv_text = models.TextField(blank=True, help_text="Full text extracted from CV")
    embedding = models.JSONField(default=list, help_text="768-dimensional embedding vector")
    cv_metadata = models.JSONField(default=dict, help_text="Additional CV metadata")
    
    def __str__(self):
        return f"{self.full_name or 'Unnamed Candidate'} - {self.email or 'No email'}"


class CV(TimestampedModel):
    """Individual CV file records"""
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='cvs')
    file_path = models.CharField(max_length=500, help_text="Path to CV file in S3/MinIO")
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=[
        ('pdf', 'PDF'),
        ('docx', 'DOCX'),
        ('doc', 'DOC'),
    ])
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Processing status
    extraction_status = models.CharField(max_length=50, default='pending', choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])
    extraction_error = models.TextField(blank=True)
    extracted_data = models.JSONField(default=dict, help_text="Extracted and structured CV data")
    
    def __str__(self):
        return f"CV - {self.candidate.full_name} - {self.file_name}"


class JobOffer(TimestampedModel):
    """Job posting/offer information"""
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE, related_name='job_offers')
    
    # Basic info
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField()
    
    # Location & Type
    location = models.CharField(max_length=200)
    job_type = models.CharField(max_length=50, choices=[
        ('full-time', 'Full-time'),
        ('part-time', 'Part-time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    ])
    remote_allowed = models.BooleanField(default=False)
    
    # Salary & Benefits
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=10, default='EUR')
    
    # Required skills and qualifications
    required_skills = models.JSONField(default=list)
    required_experience_years = models.IntegerField(default=0)
    required_education = models.CharField(max_length=200, blank=True)
    
    # AI Extracted Data
    embedding = models.JSONField(default=list, help_text="768-dimensional embedding vector")
    extracted_requirements = models.JSONField(default=dict)
    
    # Status
    status = models.CharField(max_length=50, default='open', choices=[
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('filled', 'Filled'),
    ])
    
    # Dates
    published_date = models.DateTimeField(null=True, blank=True)
    closing_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.location}"


class Match(TimestampedModel):
    """Matching results between Candidates and Job Offers"""
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='matches')
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE, related_name='matches')
    
    # Matching scores
    overall_score = models.FloatField(default=0.0, help_text="Overall matching score (0-100)")
    technical_skill_score = models.FloatField(default=0.0)
    experience_score = models.FloatField(default=0.0)
    education_score = models.FloatField(default=0.0)
    soft_skill_score = models.FloatField(default=0.0)
    
    # Detailed analysis
    match_explanation = models.TextField(blank=True, help_text="AI-generated explanation of the match")
    strengths = models.JSONField(default=list, help_text="Candidate's strengths for this role")
    gaps = models.JSONField(default=list, help_text="Gaps or concerns")
    recommendations = models.JSONField(default=list, help_text="Recommendations for hiring decision")
    
    # Status
    status = models.CharField(max_length=50, default='pending', choices=[
        ('pending', 'Pending Review'),
        ('shortlisted', 'Shortlisted'),
        ('interview', 'Interview Scheduled'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ])
    
    # Metadata
    matched_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['candidate', 'job_offer']
        ordering = ['-overall_score']
    
    def __str__(self):
        return f"Match: {self.candidate.full_name} ↔ {self.job_offer.title} ({self.overall_score}%)"


class Conversation(TimestampedModel):
    """Conversational assistant chat sessions"""
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE, related_name='conversations')
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE, related_name='conversations', null=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='conversations', null=True)
    
    title = models.CharField(max_length=200)
    
    def __str__(self):
        return f"Conversation: {self.title}"


class Message(TimestampedModel):
    """Individual messages in conversations"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=[
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ])
    content = models.TextField()
    
    # RAG metadata
    sources_used = models.JSONField(default=list, help_text="Sources referenced by RAG")
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class GeneratedDocument(TimestampedModel):
    """AI-generated documents (emails, interview questions, reports)"""
    document_type = models.CharField(max_length=50, choices=[
        ('contact_email', 'Contact Email'),
        ('interview_questions', 'Interview Questions'),
        ('candidate_summary', 'Candidate Summary'),
        ('report', 'Analysis Report'),
    ])
    
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, null=True, blank=True)
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE, null=True, blank=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, null=True, blank=True)
    
    content = models.TextField()
    metadata = models.JSONField(default=dict)
    
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.document_type} - {self.created_at}"


class Analytics(TimestampedModel):
    """Analytics and reporting data"""
    event_type = models.CharField(max_length=100)
    candidate = models.ForeignKey(Candidate, on_delete=models.SET_NULL, null=True, blank=True)
    job_offer = models.ForeignKey(JobOffer, on_delete=models.SET_NULL, null=True, blank=True)
    match = models.ForeignKey(Match, on_delete=models.SET_NULL, null=True, blank=True)
    
    event_data = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.event_type} - {self.created_at}"

