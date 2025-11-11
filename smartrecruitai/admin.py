"""
Django Admin configuration for SmartRecruitAI
"""

from django.contrib import admin
from .models import (
    Recruiter, Candidate, CV, JobOffer, Match,
    Conversation, Message, GeneratedDocument, Analytics
)


@admin.register(Recruiter)
class RecruiterAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'phone_number', 'created_at']
    search_fields = ['user__username', 'user__email', 'company_name']


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'current_position', 'status', 'availability', 'created_at']
    list_filter = ['status', 'availability', 'created_at']
    search_fields = ['full_name', 'email', 'current_position']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'file_name', 'file_type', 'extraction_status', 'created_at']
    list_filter = ['extraction_status', 'file_type']
    search_fields = ['candidate__full_name', 'file_name']


@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'recruiter', 'location', 'job_type', 'status', 'created_at']
    list_filter = ['status', 'job_type', 'created_at']
    search_fields = ['title', 'description', 'location']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'job_offer', 'overall_score', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['candidate__full_name', 'job_offer__title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recruiter', 'candidate', 'job_offer', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['content']


@admin.register(GeneratedDocument)
class GeneratedDocumentAdmin(admin.ModelAdmin):
    list_display = ['document_type', 'candidate', 'job_offer', 'created_at']
    list_filter = ['document_type', 'created_at']
    search_fields = ['content']


@admin.register(Analytics)
class AnalyticsAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'candidate', 'job_offer', 'created_at']
    list_filter = ['event_type', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

