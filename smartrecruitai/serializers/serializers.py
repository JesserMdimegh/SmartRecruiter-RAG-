"""
Django REST Framework serializers for SmartRecruitAI
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import (
    Recruiter, Candidate, CV, JobOffer, Match,
    Conversation, Message, GeneratedDocument, Analytics
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class RecruiterSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Recruiter
        fields = ['id', 'user', 'company_name', 'phone_number', 'created_at', 'updated_at']


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class CandidateDetailSerializer(serializers.ModelSerializer):
    cvs = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Candidate
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class CVSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    
    class Meta:
        model = CV
        fields = [
            'id', 'candidate', 'candidate_name', 'file_path', 'file_name', 
            'file_type', 'uploaded_by', 'extraction_status', 'extraction_error',
            'extracted_data', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'extracted_data']


class JobOfferSerializer(serializers.ModelSerializer):
    recruiter_company = serializers.CharField(source='recruiter.company_name', read_only=True)
    
    class Meta:
        model = JobOffer
        fields = [
            'id', 'recruiter', 'recruiter_company', 'title', 'description',
            'requirements', 'location', 'job_type', 'remote_allowed',
            'salary_min', 'salary_max', 'currency', 'required_skills',
            'required_experience_years', 'required_education', 'status',
            'published_date', 'closing_date', 'embedding', 'extracted_requirements',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'embedding', 'extracted_requirements']


class JobOfferCreateSerializer(serializers.ModelSerializer):
    required_skills = serializers.JSONField(default=list, allow_null=True)
    
    class Meta:
        model = JobOffer
        fields = [
            'title', 'description', 'requirements', 'location', 'job_type',
            'remote_allowed', 'salary_min', 'salary_max', 'currency',
            'required_skills', 'required_experience_years', 'required_education'
        ]
    
    def validate_required_skills(self, value):
        """Ensure required_skills is a list"""
        if value is None:
            return []
        if not isinstance(value, list):
            return [value] if value else []
        return value


class MatchSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    job_title = serializers.CharField(source='job_offer.title', read_only=True)
    
    class Meta:
        model = Match
        fields = [
            'id', 'candidate', 'candidate_name', 'job_offer', 'job_title',
            'overall_score', 'technical_skill_score', 'experience_score',
            'education_score', 'soft_skill_score', 'match_explanation',
            'strengths', 'gaps', 'recommendations', 'status', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id', 'recruiter', 'job_offer', 'candidate', 'title', 'created_at', 'updated_at']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'role', 'content', 'sources_used', 'created_at', 'updated_at']


class GeneratedDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedDocument
        fields = [
            'id', 'document_type', 'candidate', 'job_offer', 'match',
            'content', 'metadata', 'generated_by', 'created_at', 'updated_at'
        ]


class AnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analytics
        fields = [
            'id', 'event_type', 'candidate', 'job_offer', 'match',
            'event_data', 'created_at', 'updated_at'
        ]

