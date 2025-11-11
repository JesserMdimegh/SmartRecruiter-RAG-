"""
URL configuration for SmartRecruitAI
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CandidateViewSet, JobOfferViewSet, MatchViewSet,
    ConversationViewSet, CVViewSet, cv_upload_page,
    create_job_offer_page, list_job_offers_page, match_cv_page
)

router = DefaultRouter()
router.register(r'candidates', CandidateViewSet, basename='candidate')
router.register(r'job-offers', JobOfferViewSet, basename='joboffer')
router.register(r'matches', MatchViewSet, basename='match')
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'cvs', CVViewSet, basename='cv')

urlpatterns = [
    path('api/', include(router.urls)),
    path('upload-cv/', cv_upload_page, name='cv_upload'),
    path('create-job/', create_job_offer_page, name='create_job'),
    path('list-jobs/', list_job_offers_page, name='list_jobs'),
    path('match-cv/', match_cv_page, name='match_cv'),
]

